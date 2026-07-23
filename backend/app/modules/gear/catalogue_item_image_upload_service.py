"""Service for handling catalogue item image uploads."""

import ipaddress
import logging
import socket
import uuid
from io import BytesIO
from urllib.parse import urlparse

from fastapi import HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.storage.exceptions import CorruptedImageError
from app.core.storage.factory import get_storage_adapter
from app.core.storage.image_processor import ImageProcessor
from app.modules.auth.db_models import UserDB
from app.modules.gear.catalogue_item_image_repository import (
    CatalogueItemImageRepository,
)
from app.modules.gear.db_models import GlobalCatalogueItemDB
from app.modules.settings.db_models import UserSettingsDB

# Optional import for MIME type detection
try:
    import magic

    HAS_MAGIC = True
except ImportError:  # pragma: no cover
    HAS_MAGIC = False

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


class CatalogueItemImageUploadService:
    """Service for handling image uploads for global catalogue items."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage = get_storage_adapter()
        self.allowed_mime_types = settings.storage.allowed_mime_types
        self.repository = CatalogueItemImageRepository(db)

    async def _ensure_catalogue_item_exists(self, catalogue_item_id: str) -> None:
        result = await self.db.execute(select(GlobalCatalogueItemDB).where(GlobalCatalogueItemDB.id == catalogue_item_id))
        item = result.scalars().first()
        if not item:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Catalogue item not found")

    def _validate_url_for_ssrf(self, url: str) -> None:
        """Validate URL to prevent SSRF (copy of ImageUploadService logic)."""
        try:
            parsed = urlparse(url)
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid URL format") from exc

        if parsed.scheme not in ("http", "https"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only HTTP and HTTPS URLs are allowed",
            )

        if not parsed.netloc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid URL format: missing hostname",
            )

        hostname = parsed.netloc.split(":")[0].lower()

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

        try:
            addr_info = socket.getaddrinfo(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
            if not addr_info:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Could not resolve hostname",
                )

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

                if ip.is_private:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Private IP addresses are not allowed",
                    )
                if ip.is_link_local:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Link-local addresses are not allowed",
                    )
                if ip.is_loopback:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Loopback addresses are not allowed",
                    )
                if ip.is_reserved:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Reserved IP addresses are not allowed",
                    )
        except socket.gaierror as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not resolve hostname",
            ) from exc

    async def _get_max_file_size_for_user(self, user_id: str) -> int:
        """Reuse feature-limits logic used for item images."""
        from app.modules.feature_limits.repository import FeatureLimitRepository

        result = await self.db.execute(select(UserDB).where(UserDB.id == user_id))
        user = result.scalars().first()
        if not user:
            return settings.storage.max_file_size

        if user.is_owner:
            role = "owner"
        elif user.is_admin:
            role = "admin"
        elif user.is_premium:
            role = "premium"
        else:
            role = "user"

        feature_limit_repo = FeatureLimitRepository(self.db)
        feature_limit = await feature_limit_repo.get_by_role(role)
        if feature_limit:
            return feature_limit.storage_limit_bytes

        if user.is_admin or user.is_owner:
            return settings.storage.max_file_size_admin
        return settings.storage.max_file_size

    async def _get_user_image_processor(self, user_id: str) -> ImageProcessor:
        result = await self.db.execute(select(UserSettingsDB).where(UserSettingsDB.user_id == user_id))
        user_settings = result.scalars().first()
        processing_mode = (user_settings.image_processing_mode if user_settings else None) or "balanced"
        mode_config = IMAGE_PROCESSING_MODES.get(processing_mode, IMAGE_PROCESSING_MODES["balanced"])
        return ImageProcessor(
            max_width=mode_config["max_width"],
            max_height=mode_config["max_height"],
            jpeg_quality=mode_config["jpeg_quality"],
            convert_to_webp=settings.storage.convert_to_webp,
        )

    async def validate_upload(self, file: UploadFile, catalogue_item_id: str, user_id: str) -> None:
        await self._ensure_catalogue_item_exists(catalogue_item_id)

        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        max_file_size = await self._get_max_file_size_for_user(user_id)
        if file_size > max_file_size:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds maximum allowed size of {max_file_size / 1024 / 1024:.1f} MB",
            )

        if file.content_type and file.content_type not in self.allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type {file.content_type} not allowed. Allowed types: {', '.join(self.allowed_mime_types)}",
            )

        existing_count = await self.repository.count_by_catalogue_item(catalogue_item_id)
        if existing_count >= settings.storage.max_files_per_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {settings.storage.max_files_per_item} images per item",
            )

        if settings.storage.type == "local":
            available_space = await self.storage.get_available_space()
            if available_space and available_space < file_size:
                raise HTTPException(
                    status_code=status.HTTP_507_INSUFFICIENT_STORAGE,
                    detail="Insufficient storage space",
                )

    async def upload_image(
        self,
        file: UploadFile,
        catalogue_item_id: str,
        user_id: str,
        is_primary: bool = False,
    ) -> dict:
        content = await file.read()
        original_filename = file.filename or "uploaded-image"
        return await self._process_and_store_image(
            content=content,
            catalogue_item_id=catalogue_item_id,
            user_id=user_id,
            original_filename=original_filename,
            is_primary=is_primary,
        )

    async def delete_image(self, image_id: str) -> bool:
        image = await self.repository.get_by_id(image_id)
        if not image:
            return False

        if image.storage_type != "external" and image.file_path:
            try:
                await self.storage.delete(image.file_path)
            except Exception as exc:  # pragma: no cover
                logger.error("Failed to delete file from storage: %s", exc)

        return await self.repository.delete(image_id)

    async def get_images(self, catalogue_item_id: str) -> list[dict]:
        await self._ensure_catalogue_item_exists(catalogue_item_id)
        images = await self.repository.get_by_catalogue_item(catalogue_item_id)
        result: list[dict] = []
        for img in images:
            url = img.external_url or await self.storage.get_url(img.file_path)
            result.append(
                {
                    "id": img.id,
                    "catalogueItemId": img.catalogue_item_id,
                    "userId": img.user_id,
                    "url": url,
                    "fileName": img.file_name,
                    "fileSize": img.file_size,
                    "mimeType": img.mime_type,
                    "width": img.width,
                    "height": img.height,
                    "isPrimary": img.is_primary,
                    "order": img.order,
                    "createdAt": img.created_at.isoformat(),
                    "updatedAt": img.updated_at.isoformat(),
                }
            )
        return result

    async def reorder_images(self, catalogue_item_id: str, image_orders: list[dict]) -> None:
        await self._ensure_catalogue_item_exists(catalogue_item_id)
        for order_update in image_orders:
            await self.repository.update(order_update["id"], {"order": order_update["order"]})

    async def toggle_primary_image(self, catalogue_item_id: str, image_id: str) -> bool:
        await self._ensure_catalogue_item_exists(catalogue_item_id)

        image = await self.repository.get_by_id(image_id)
        if not image:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found")

        if image.is_primary:
            await self.repository.update(image_id, {"is_primary": False})
            return False

        await self.repository.unset_primary_for_catalogue_item(catalogue_item_id)
        await self.repository.update(image_id, {"is_primary": True})
        return True

    async def upload_image_from_url(
        self,
        image_url: str,
        catalogue_item_id: str,
        user_id: str,
        is_primary: bool = False,
        host_locally: bool = True,
    ) -> dict:
        await self._ensure_catalogue_item_exists(catalogue_item_id)

        existing_count = await self.repository.count_by_catalogue_item(catalogue_item_id)
        if existing_count >= settings.storage.max_files_per_item:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Maximum {settings.storage.max_files_per_item} images per item",
            )

        # Always validate URL for SSRF protection
        self._validate_url_for_ssrf(image_url)

        if host_locally:
            # SECURITY:
            # We intentionally do NOT fetch arbitrary remote URLs server-side for catalogue items,
            # to prevent SSRF (CodeQL: py/full-ssrf). Use file upload instead.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Hosting catalogue images locally from URL is disabled. Please upload a file instead.",
            )

        if is_primary:
            await self.repository.unset_primary_for_catalogue_item(catalogue_item_id)
        else:
            existing_primary = await self.repository.get_primary_image(catalogue_item_id)
            if not existing_primary:
                is_primary = True

        original_filename = image_url.rsplit("/", 1)[-1] or "remote-image"
        image_record = await self.repository.create(
            {
                "catalogue_item_id": catalogue_item_id,
                "user_id": user_id,
                "storage_type": "external",
                "file_path": "",
                "file_name": original_filename,
                "file_size": 0,
                "mime_type": "image/*",
                "width": None,
                "height": None,
                "is_primary": is_primary,
                "order": await self.repository.get_next_order(catalogue_item_id),
                "is_processed": False,
                "original_file_size": None,
                "external_url": image_url,
            }
        )
        return {
            "id": image_record.id,
            "catalogueItemId": catalogue_item_id,
            "userId": user_id,
            "url": image_url,
            "fileName": original_filename,
            "fileSize": 0,
            "mimeType": "image/*",
            "width": None,
            "height": None,
            "isPrimary": is_primary,
            "order": image_record.order,
            "createdAt": image_record.created_at.isoformat(),
            "updatedAt": image_record.updated_at.isoformat(),
        }

    async def _process_and_store_image(
        self,
        content: bytes,
        catalogue_item_id: str,
        user_id: str,
        original_filename: str,
        is_primary: bool,
    ) -> dict:
        detected_mime = None
        if HAS_MAGIC:
            try:
                mime = magic.Magic(mime=True)
                detected_mime = mime.from_buffer(content)
            except Exception:  # pragma: no cover
                detected_mime = None

        if not detected_mime:
            try:
                img = Image.open(BytesIO(content))
                format_lower = img.format.lower() if img.format else None
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
            except HTTPException:
                raise
            except Exception as exc:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to detect file type",
                ) from exc

        if detected_mime not in self.allowed_mime_types:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Invalid file type. Detected: {detected_mime}",
            )

        processor = await self._get_user_image_processor(user_id)
        if not await processor.validate_image(content):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or corrupted image file",
            )

        original_size = len(content)

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
            try:
                img = Image.open(BytesIO(content))
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

        file_ext = MIME_TO_EXTENSION.get(detected_mime, ".jpg")
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        destination_path = f"catalogue-items/{catalogue_item_id}/{unique_filename}"

        stored_path = None
        try:
            stored_path = await self.storage.upload(
                content,
                destination_path,
                detected_mime,
                metadata={
                    "catalogue_item_id": catalogue_item_id,
                    "user_id": user_id,
                    "original_filename": original_filename,
                },
            )

            if is_primary:
                await self.repository.unset_primary_for_catalogue_item(catalogue_item_id)
            else:
                existing_primary = await self.repository.get_primary_image(catalogue_item_id)
                if not existing_primary:
                    is_primary = True

            image_record = await self.repository.create(
                {
                    "catalogue_item_id": catalogue_item_id,
                    "user_id": user_id,
                    "storage_type": settings.storage.type,
                    "file_path": stored_path,
                    "file_name": original_filename,
                    "file_size": processed_size,
                    "mime_type": detected_mime,
                    "width": width,
                    "height": height,
                    "is_primary": is_primary,
                    "order": await self.repository.get_next_order(catalogue_item_id),
                    "is_processed": settings.storage.enable_processing,
                    "original_file_size": (original_size if settings.storage.enable_processing else None),
                    "external_url": None,
                }
            )

            url = await self.storage.get_url(stored_path)
            return {
                "id": image_record.id,
                "catalogueItemId": catalogue_item_id,
                "userId": user_id,
                "url": url,
                "fileName": original_filename,
                "fileSize": processed_size,
                "mimeType": detected_mime,
                "width": width,
                "height": height,
                "isPrimary": is_primary,
                "order": image_record.order,
                "createdAt": image_record.created_at.isoformat(),
                "updatedAt": image_record.updated_at.isoformat(),
            }
        except HTTPException:
            if stored_path:
                try:
                    await self.storage.delete(stored_path)
                except Exception:  # pragma: no cover
                    pass
            raise
        except Exception as exc:  # pragma: no cover
            if stored_path:
                try:
                    await self.storage.delete(stored_path)
                except Exception:
                    pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to upload image",
            ) from exc
