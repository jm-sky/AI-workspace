"""Service for handling image uploads with proper error handling and transaction safety."""

import ipaddress
import logging
import socket
import uuid
from io import BytesIO
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy.ext.asyncio import AsyncSession

# Optional import for MIME type detection
try:
    import magic

    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False
    logger = logging.getLogger(__name__)
    logger.warning("python-magic not available, will use Pillow for MIME type detection")

from sqlalchemy import select

from app.core.config import settings
from app.core.storage.exceptions import CorruptedImageError
from app.core.storage.factory import get_storage_adapter
from app.core.storage.image_processor import ImageProcessor
from app.modules.auth.db_models import UserDB
from app.modules.gear.item_image_repository import ItemImageRepository
from app.modules.gear.item_image_schemas import ItemImageResponse
from app.modules.settings.db_models import UserSettingsDB

logger = logging.getLogger(__name__)

# MIME type to extension mapping (centralized constant)
MIME_TO_EXTENSION = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

# Image processing mode configurations
IMAGE_PROCESSING_MODES = {
    "high_quality": {
        "max_width": 2560,
        "max_height": 2560,
        "jpeg_quality": 95,
    },
    "balanced": {
        "max_width": 1200,
        "max_height": 1200,
        "jpeg_quality": 90,
    },
    "storage_saver": {
        "max_width": 800,
        "max_height": 800,
        "jpeg_quality": 80,
    },
}


class ImageUploadService:
    """Service for handling image uploads."""

    def __init__(self, db: AsyncSession):
        """
        Initialize image upload service.

        Args:
            db: Database session
        """
        self.db = db
        self.storage = get_storage_adapter()
        # Processor will be created dynamically based on user settings
        self.max_file_size = settings.storage.max_file_size
        self.max_file_size_admin = settings.storage.max_file_size_admin
        self.allowed_mime_types = settings.storage.allowed_mime_types
        self.repository = ItemImageRepository(db)

    def _validate_url_for_ssrf(self, url: str) -> None:
        """
        Validate URL to prevent SSRF (Server-Side Request Forgery) attacks.

        Blocks:
        - Private/internal IP addresses
        - Localhost addresses
        - Link-local addresses
        - Non-HTTP/HTTPS schemes
        - Invalid URLs

        Args:
            url: URL to validate

        Raises:
            HTTPException: If URL is unsafe or invalid
        """
        try:
            parsed = urlparse(url)
        except Exception as exc:
            logger.error("Invalid URL format: %s", url)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL format",
            ) from exc

        # Only allow HTTP and HTTPS schemes
        if parsed.scheme not in ("http", "https"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only HTTP and HTTPS URLs are allowed",
            )

        # Must have a hostname
        if not parsed.netloc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL format: missing hostname",
            )

        # Extract hostname (remove port if present)
        hostname = parsed.netloc.split(":")[0].lower()

        # Block localhost and common localhost variants
        blocked_hostnames = {
            "localhost",
            "127.0.0.1",
            "0.0.0.0",
            "::1",
            "[::1]",
        }
        if hostname in blocked_hostnames:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Localhost URLs are not allowed",
            )

        # Resolve hostname to IP address and check if it's private
        try:
            # Use getaddrinfo to resolve hostname (handles both IPv4 and IPv6)
            addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            if not addr_info:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not resolve hostname",
                )

            # Check all resolved IPs
            for family, _, _, _, sockaddr in addr_info:
                if family == socket.AF_INET:
                    ip_str = sockaddr[0]
                elif family == socket.AF_INET6:
                    ip_str = sockaddr[0]
                else:
                    continue

                try:
                    ip = ipaddress.ip_address(ip_str)
                except ValueError:
                    continue

                # Block private IP ranges
                if ip.is_private:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Private IP addresses are not allowed",
                    )

                # Block link-local addresses
                if ip.is_link_local:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Link-local addresses are not allowed",
                    )

                # Block loopback addresses
                if ip.is_loopback:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Loopback addresses are not allowed",
                    )

                # Block reserved addresses (includes multicast, etc.)
                if ip.is_reserved:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Reserved IP addresses are not allowed",
                    )

        except socket.gaierror as exc:
            logger.error("Failed to resolve hostname %s: %s", hostname, exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not resolve hostname",
            ) from exc
        except HTTPException:
            # Re-raise HTTP exceptions (our validation failures)
            raise
        except Exception as exc:
            logger.error("Unexpected error during URL validation: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL validation failed",
            ) from exc

    async def _get_max_file_size_for_user(self, user_id: str) -> int:
        """
        Get maximum file size for user based on role from feature_limits table.

        Args:
            user_id: User ID

        Returns:
            Maximum file size in bytes from feature_limits table, or fallback to config
        """
        from app.modules.feature_limits.repository import FeatureLimitRepository

        result = await self.db.execute(select(UserDB).where(UserDB.id == user_id))
        user = result.scalars().first()
        if not user:
            return self.max_file_size

        # Determine user role
        if user.is_owner:
            role = "owner"
        elif user.is_admin:
            role = "admin"
        elif user.is_premium:
            role = "premium"
        else:
            role = "user"

        # Get limit from database
        feature_limit_repo = FeatureLimitRepository(self.db)
        feature_limit = await feature_limit_repo.get_by_role(role)

        if feature_limit:
            return feature_limit.storage_limit_bytes

        # Fallback to config if limit not found in database
        if user.is_admin or user.is_owner:
            return self.max_file_size_admin
        return self.max_file_size

    async def _get_user_image_processor(self, user_id: str) -> ImageProcessor:
        """
        Get image processor configured for user's processing mode.

        Args:
            user_id: User ID

        Returns:
            ImageProcessor instance configured for user's mode
        """
        # Get user settings
        result = await self.db.execute(select(UserSettingsDB).where(UserSettingsDB.user_id == user_id))
        user_settings = result.scalars().first()

        # Get processing mode (default to 'balanced' if not set)
        processing_mode = (user_settings.image_processing_mode if user_settings else None) or "balanced"

        # Get configuration for mode
        mode_config = IMAGE_PROCESSING_MODES.get(processing_mode, IMAGE_PROCESSING_MODES["balanced"])

        # Create processor with user's settings
        return ImageProcessor(
            max_width=mode_config["max_width"],
            max_height=mode_config["max_height"],
            jpeg_quality=mode_config["jpeg_quality"],
            convert_to_webp=settings.storage.convert_to_webp,
        )

    async def validate_upload(self, file: UploadFile, item_id: str, user_id: str) -> None:
        """
        Validate file upload constraints.

        Args:
            file: Uploaded file
            item_id: Item ID to upload image for
            user_id: User ID (to check admin status for file size limit)

        Raises:
            HTTPException: If validation fails
        """
        # Check file size (use user-specific limit)
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset

        max_file_size = await self._get_max_file_size_for_user(user_id)
        if file_size > max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {max_file_size / 1024 / 1024:.1f} MB",
            )

        # Check MIME type (preliminary check based on content-type header)
        if file.content_type and file.content_type not in self.allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(self.allowed_mime_types)}",
            )

        # Check number of existing images for item
        existing_count = await self.repository.count_by_item(item_id)
        if existing_count >= settings.storage.max_files_per_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {settings.storage.max_files_per_item} images per item",
            )

        # Check available storage space (for local storage)
        if settings.storage.type == "local":
            available_space = await self.storage.get_available_space()
            if available_space and available_space < file_size:
                raise HTTPException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail="Insufficient storage space",
                )

    async def upload_image(self, file: UploadFile, item_id: str, user_id: str, is_primary: bool = False) -> dict:
        """
        Upload and process image with transaction safety.

        Args:
            file: Uploaded file
            item_id: Item ID
            user_id: User ID (uploader)
            is_primary: Whether this should be the primary image

        Returns:
            Image metadata dictionary

        Raises:
            HTTPException: If upload or processing fails
        """
        # Read file content
        content = await file.read()
        original_filename = file.filename or "uploaded-image"

        return await self._process_and_store_image(
            content=content,
            item_id=item_id,
            user_id=user_id,
            original_filename=original_filename,
            is_primary=is_primary,
        )

    async def delete_image(self, image_id: str, user_id: str) -> bool:
        """
        Delete image by ID.

        Args:
            image_id: Image ID
            user_id: User ID (for authorization check)

        Returns:
            True if deleted successfully, False if not found
        """
        image = await self.repository.get_by_id(image_id)

        if not image:
            return False

        # Delete from storage only if not external URL (continue even if this fails)
        if image.storage_type != "external" and image.file_path:
            try:
                await self.storage.delete(image.file_path)
            except Exception as e:
                logger.error(f"Failed to delete file from storage: {e}")

        # Delete from database
        await self.repository.delete(image_id)

        return True

    async def delete_all_item_images(self, item_id: str) -> int:
        """
        Delete all images for an item (used when item is deleted).

        Args:
            item_id: Item ID

        Returns:
            Number of images deleted
        """
        images = await self.repository.get_by_item(item_id)
        deleted_count = 0

        for image in images:
            # Delete from storage only if not external URL (continue even if this fails)
            if image.storage_type != "external" and image.file_path:
                try:
                    await self.storage.delete(image.file_path)
                except Exception as e:
                    logger.error(f"Failed to delete image file from storage (item_id={item_id}, image_id={image.id}): {e}")

            # Delete from database
            try:
                await self.repository.delete(image.id)
                deleted_count += 1
            except Exception as e:
                logger.error(f"Failed to delete image record from database (item_id={item_id}, image_id={image.id}): {e}")

        if deleted_count > 0:
            logger.info(f"Deleted {deleted_count} image(s) for item {item_id}")

        return deleted_count

    async def reorder_images(self, item_id: str, image_orders: list[dict]) -> bool:
        """
        Reorder images for an item.

        Args:
            item_id: Item ID
            image_orders: List of {"id": "uuid", "order": 0} dictionaries

        Returns:
            True if successful
        """
        for item in image_orders:
            await self.repository.update(item["id"], {"order": item["order"]})
        return True

    async def toggle_primary_image(self, item_id: str, image_id: str) -> bool:
        """
        Toggle primary status for image (set if not primary, unset if already primary).

        Args:
            item_id: Item ID
            image_id: Image ID to toggle primary status

        Returns:
            True if image is now primary, False if it was unset
        """
        # Get current image to check if it's already primary
        image = await self.repository.get_by_id(image_id)
        if not image:
            raise ValueError(f"Image {image_id} not found")

        is_currently_primary = image.is_primary

        if is_currently_primary:
            # If already primary, unset it
            await self.repository.update(image_id, {"is_primary": False})
            return False
        else:
            # If not primary, unset all other primaries and set this one
            await self.repository.unset_primary_for_item(item_id)
            await self.repository.update(image_id, {"is_primary": True})
            return True

    async def get_item_images(self, item_id: str) -> list[ItemImageResponse]:
        """
        Get all images for an item with URLs.

        Args:
            item_id: Item ID

        Returns:
            List of image response objects with URLs
        """
        images = await self.repository.get_by_item(item_id)

        result = []
        for img in images:
            # If external_url exists, use it. Otherwise, get URL from storage.
            if img.external_url:
                url = img.external_url
            else:
                url = await self.storage.get_url(img.file_path)
            # Use Pydantic schema to ensure proper field name conversion (is_primary -> isPrimary)
            image_response = ItemImageResponse(
                id=img.id,
                itemId=img.item_id,
                userId=img.user_id,
                url=url,
                fileName=img.file_name,
                fileSize=img.file_size,
                mimeType=img.mime_type,
                width=img.width,
                height=img.height,
                isPrimary=img.is_primary,
                order=img.order,
                createdAt=img.created_at.isoformat(),
                updatedAt=img.updated_at.isoformat(),
            )
            result.append(image_response)

        return result

    async def upload_image_from_url(
        self,
        image_url: str,
        item_id: str,
        user_id: str,
        is_primary: bool = False,
        host_locally: bool = True,
    ) -> dict:
        """
        Create item image from external URL.

        Args:
            image_url: External image URL
            item_id: Item ID
            user_id: User ID (uploader)
            is_primary: Whether this should be the primary image
            host_locally: If True, download and store image. If False, only save external URL.

        Returns:
            Image metadata dictionary

        Raises:
            HTTPException: If download or processing fails
        """
        # Check max images per item
        existing_count = await self.repository.count_by_item(item_id)
        if existing_count >= settings.storage.max_files_per_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {settings.storage.max_files_per_item} images per item",
            )

        if host_locally:
            # Validate URL for SSRF protection before downloading
            self._validate_url_for_ssrf(image_url)

            # Download and store image (existing behavior)
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.get(image_url)
                    response.raise_for_status()

                    content = response.content
            except httpx.HTTPError as exc:
                logger.error("Failed to download image from URL %s: %s", image_url, exc)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to download image from URL",
                ) from exc

            # Enforce max file size (use user-specific limit)
            file_size = len(content)
            max_file_size = await self._get_max_file_size_for_user(user_id)
            if file_size > max_file_size:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File size exceeds maximum allowed size of {max_file_size / 1024 / 1024:.1f} MB",
                )

            # Check available storage for local adapter
            if settings.storage.type == "local":
                available_space = await self.storage.get_available_space()
                if available_space and available_space < file_size:
                    raise HTTPException(
                        status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                        detail="Insufficient storage space",
                    )

            # Use last part of URL as original filename, if possible
            original_filename = image_url.rsplit("/", 1)[-1] or "remote-image"

            return await self._process_and_store_image(
                content=content,
                item_id=item_id,
                user_id=user_id,
                original_filename=original_filename,
                is_primary=is_primary,
            )
        else:
            # Only save external URL (new behavior)
            # Validate URL for SSRF protection
            self._validate_url_for_ssrf(image_url)

            # Use last part of URL as original filename, if possible
            original_filename = image_url.rsplit("/", 1)[-1] or "remote-image"

            # If this is primary or no primary exists, unset other primaries
            if is_primary:
                await self.repository.unset_primary_for_item(item_id)
            else:
                # Check if any primary exists
                existing_primary = await self.repository.get_primary_image(item_id)
                if not existing_primary:
                    # First image should be primary
                    is_primary = True

            # Create database record with external URL
            image_record = await self.repository.create(
                {
                    "item_id": item_id,
                    "user_id": user_id,
                    "storage_type": "external",  # Special storage type for external URLs
                    "file_path": "",  # Empty for external URLs
                    "file_name": original_filename,
                    "file_size": 0,  # Unknown size for external URLs
                    "mime_type": "image/*",  # Unknown MIME type for external URLs
                    "width": None,
                    "height": None,
                    "is_primary": is_primary,
                    "order": await self.repository.get_next_order(item_id),
                    "is_processed": False,
                    "original_file_size": None,
                    "external_url": image_url,
                }
            )

            return {
                "id": image_record.id,
                "url": image_url,  # Return external URL directly
                "file_name": original_filename,
                "file_size": 0,
                "mime_type": "image/*",
                "width": None,
                "height": None,
                "is_primary": is_primary,
                "order": image_record.order,
                "created_at": image_record.created_at.isoformat(),
                "updated_at": image_record.updated_at.isoformat(),
            }

    async def _process_and_store_image(
        self,
        content: bytes,
        item_id: str,
        user_id: str,
        original_filename: str,
        is_primary: bool,
    ) -> dict:
        """Shared implementation for processing, storing and persisting image metadata."""
        # Validate MIME type using python-magic (magic numbers) or Pillow as fallback
        detected_mime = None
        if HAS_MAGIC:
            try:
                mime = magic.Magic(mime=True)
                detected_mime = mime.from_buffer(content)
            except Exception as e:  # pragma: no cover - defensive logging
                logger.warning(
                    "Failed to detect MIME type with magic: %s, falling back to Pillow",
                    e,
                )
                detected_mime = None

        # Fallback to Pillow if magic is not available or failed
        if not detected_mime:
            try:
                import asyncio

                img = await asyncio.to_thread(Image.open, BytesIO(content))
                format_lower = img.format.lower() if img.format else None
                # Map Pillow format to MIME type
                format_to_mime = {
                    "jpeg": "image/jpeg",
                    "jpg": "image/jpeg",
                    "png": "image/png",
                    "webp": "image/webp",
                    "gif": "image/gif",
                }
                detected_mime = format_to_mime.get(format_lower) if format_lower else None
                if not detected_mime:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to detect file type",
                    )
            except Exception as e:
                logger.error("Failed to detect MIME type with Pillow: %s", e)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to detect file type",
                ) from e

        if detected_mime not in self.allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Invalid file type. Detected: {detected_mime}",
            )

        # Get user's image processor
        processor = await self._get_user_image_processor(user_id)

        # Validate image integrity
        if not await processor.validate_image(content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or corrupted image file",
            )

        original_size = len(content)

        # Process image if enabled
        if settings.storage.enable_processing:
            try:
                content, detected_mime, width, height = await processor.process_image(content, detected_mime)
                processed_size = len(content)
            except CorruptedImageError as e:
                # Handle corrupted/truncated images gracefully
                logger.warning(f"Corrupted image file uploaded: {e}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Image file is corrupted or truncated. Please upload a valid image file.",
                ) from e
        else:
            # Get dimensions without processing (run in thread pool)
            import asyncio

            try:
                img = await asyncio.to_thread(Image.open, BytesIO(content))
                img.load()  # Load image to detect truncation
                width, height = img.size
            except OSError as e:
                # Handle truncated/corrupted images
                error_msg = str(e).lower()
                if "truncated" in error_msg or "cannot identify" in error_msg:
                    logger.warning(f"Corrupted image file uploaded: {e}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Image file is corrupted or truncated. Please upload a valid image file.",
                    ) from e
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid image file. Please upload a valid image file.",
                ) from e
            processed_size = original_size

        # Generate unique filename
        file_ext = MIME_TO_EXTENSION.get(detected_mime, ".jpg")
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        destination_path = f"items/{item_id}/{unique_filename}"

        # Upload to storage with rollback on failure
        stored_path = None
        try:
            stored_path = await self.storage.upload(
                content,
                destination_path,
                detected_mime,
                metadata={
                    "item_id": item_id,
                    "user_id": user_id,
                    "original_filename": original_filename,
                },
            )

            # If this is primary or no primary exists, unset other primaries
            if is_primary:
                await self.repository.unset_primary_for_item(item_id)
            else:
                # Check if any primary exists
                existing_primary = await self.repository.get_primary_image(item_id)
                if not existing_primary:
                    # First image should be primary
                    is_primary = True

            # Create database record
            image_record = await self.repository.create(
                {
                    "item_id": item_id,
                    "user_id": user_id,
                    "storage_type": settings.storage.type,
                    "file_path": stored_path,
                    "file_name": original_filename,
                    "file_size": processed_size,
                    "mime_type": detected_mime,
                    "width": width,
                    "height": height,
                    "is_primary": is_primary,
                    "order": await self.repository.get_next_order(item_id),
                    "is_processed": settings.storage.enable_processing,
                    "original_file_size": (original_size if settings.storage.enable_processing else None),
                }
            )

            # Get accessible URL
            url = await self.storage.get_url(stored_path)

            return {
                "id": image_record.id,
                "url": url,
                "file_name": original_filename,
                "file_size": processed_size,
                "mime_type": detected_mime,
                "width": width,
                "height": height,
                "is_primary": is_primary,
                "order": image_record.order,
            }

        except Exception as e:  # pragma: no cover - defensive rollback path
            # Rollback: delete uploaded file if database insert failed
            if stored_path:
                try:
                    await self.storage.delete(stored_path)
                    logger.info("Rolled back uploaded file: %s", stored_path)
                except Exception as cleanup_error:
                    logger.error(
                        "Failed to cleanup uploaded file %s: %s",
                        stored_path,
                        cleanup_error,
                    )

            logger.error("Image upload failed: %s", e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload image",
            ) from e
