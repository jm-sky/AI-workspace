"""Upload, store, and resolve chat attachments."""

from __future__ import annotations

import base64
import io
import logging
from datetime import UTC, datetime

import magic
from fastapi import HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.core.config import settings
from app.core.storage.exceptions import CorruptedImageError
from app.core.storage.factory import get_storage_adapter
from app.core.storage.image_processor import ImageProcessor
from app.modules.agent.db_models import ChatAttachment
from app.modules.agent.schemas_attachments import ChatAttachmentResponse
from app.modules.tenants.service import TenantContext

logger = logging.getLogger(__name__)

IMAGE_MIME_TYPES = frozenset({"image/jpeg", "image/png", "image/webp", "image/gif"})
# Stages 1–3: images only. text/pdf allow-list reserved for later stages.
ALLOWED_MIME_TYPES = IMAGE_MIME_TYPES
REJECTED_MIME_TYPES = frozenset({"image/svg+xml", "text/html", "application/xhtml+xml"})

MIME_TO_EXTENSION = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
}

# Cap decompression bombs (Pillow default is ~89M pixels).
Image.MAX_IMAGE_PIXELS = 40_000_000


class ChatAttachmentService:
    """Validate, process, and persist chat attachments."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.storage = get_storage_adapter()
        self._cfg = settings.attachments

    async def upload_image(
        self,
        *,
        tenant_ctx: TenantContext,
        file: UploadFile,
        session_id: str | None = None,
    ) -> ChatAttachmentResponse:
        content = await self._read_limited(file, self._cfg.max_file_bytes)
        display_name = (file.filename or "image").strip() or "image"
        # Never use client filename for paths — sanitize for display only.
        display_name = display_name.replace("\x00", "")[:255]

        mime = self._detect_mime(content)
        if mime in REJECTED_MIME_TYPES or mime not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file type: {mime}",
            )

        self._verify_image(content)

        model_processor = ImageProcessor(
            max_width=self._cfg.model_max_edge,
            max_height=self._cfg.model_max_edge,
            jpeg_quality=85,
            convert_to_webp=False,
        )
        thumb_processor = ImageProcessor(
            max_width=self._cfg.thumbnail_max_edge,
            max_height=self._cfg.thumbnail_max_edge,
            jpeg_quality=80,
            convert_to_webp=True,
        )

        try:
            processed, out_mime, width, height = await model_processor.process_image(content, mime)
            thumb_bytes, thumb_mime, _, _ = await thumb_processor.process_image(content, mime)
        except CorruptedImageError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except Image.DecompressionBombError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image dimensions exceed safe limits",
            ) from exc

        attachment_id = generate_id()
        ext = MIME_TO_EXTENSION.get(out_mime, ".jpg")
        storage_path = f"attachments/{tenant_ctx.tenant_id}/{attachment_id}{ext}"
        thumb_ext = MIME_TO_EXTENSION.get(thumb_mime, ".webp")
        thumbnail_path = f"attachments/{tenant_ctx.tenant_id}/{attachment_id}_thumb{thumb_ext}"

        await self.storage.upload(processed, storage_path, out_mime)
        await self.storage.upload(thumb_bytes, thumbnail_path, thumb_mime)

        now = datetime.now(UTC)
        row = ChatAttachment(
            id=attachment_id,
            owner_user_id=tenant_ctx.user_id,
            tenant_id=tenant_ctx.tenant_id,
            session_id=session_id,
            run_id=None,
            kind="image",
            original_filename=display_name,
            mime_type=out_mime,
            size_bytes=len(processed),
            storage_path=storage_path,
            thumbnail_path=thumbnail_path,
            width=width,
            height=height,
            extracted_text=None,
            extracted_chars=None,
            created_at=now,
        )
        self.db.add(row)
        await self.db.commit()
        await self.db.refresh(row)
        return self._to_response(row)

    async def get_owned(
        self,
        attachment_id: str,
        *,
        tenant_ctx: TenantContext,
    ) -> ChatAttachment | None:
        result = await self.db.execute(
            select(ChatAttachment).where(
                ChatAttachment.id == attachment_id,
                ChatAttachment.owner_user_id == tenant_ctx.user_id,
                ChatAttachment.tenant_id == tenant_ctx.tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def delete_owned(
        self,
        attachment_id: str,
        *,
        tenant_ctx: TenantContext,
    ) -> bool:
        row = await self.get_owned(attachment_id, tenant_ctx=tenant_ctx)
        if row is None:
            return False
        if row.run_id is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Attachment already used in a message",
            )
        await self.storage.delete(row.storage_path)
        if row.thumbnail_path:
            await self.storage.delete(row.thumbnail_path)
        await self.db.delete(row)
        await self.db.commit()
        return True

    async def load_for_message(
        self,
        attachment_ids: list[str],
        *,
        tenant_ctx: TenantContext,
    ) -> list[ChatAttachment]:
        if not attachment_ids:
            return []
        if len(attachment_ids) > self._cfg.max_per_message:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"At most {self._cfg.max_per_message} attachments per message",
            )
        # Preserve request order, reject duplicates / missing / foreign.
        seen: set[str] = set()
        ordered: list[ChatAttachment] = []
        total_bytes = 0
        for aid in attachment_ids:
            if aid in seen:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Duplicate attachment id",
                )
            seen.add(aid)
            row = await self.get_owned(aid, tenant_ctx=tenant_ctx)
            if row is None:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Attachment not found: {aid}",
                )
            if row.run_id is not None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Attachment already used: {aid}",
                )
            total_bytes += row.size_bytes
            if total_bytes > self._cfg.max_total_bytes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Total attachment size exceeds limit",
                )
            ordered.append(row)
        return ordered

    async def bind_to_run(
        self,
        attachments: list[ChatAttachment],
        *,
        run_id: str,
        session_id: str,
    ) -> None:
        if not attachments:
            return
        ids = [a.id for a in attachments]
        await self.db.execute(
            update(ChatAttachment)
            .where(ChatAttachment.id.in_(ids))
            .values(run_id=run_id, session_id=session_id)
        )
        await self.db.commit()

    async def build_user_content(
        self,
        message: str,
        attachments: list[ChatAttachment],
    ) -> str | list[dict]:
        """Return OpenAI-style content: string when no files, else multimodal parts."""
        if not attachments:
            return message

        parts: list[dict] = [{"type": "text", "text": message}]
        for att in attachments:
            if att.kind == "image":
                raw = await self.storage.download(att.storage_path)
                b64 = base64.b64encode(raw).decode("ascii")
                parts.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:{att.mime_type};base64,{b64}"},
                    }
                )
            elif att.extracted_text:
                parts.append(
                    {
                        "type": "text",
                        "text": (
                            f'<attachment name="{att.original_filename}">\n'
                            f"{att.extracted_text}\n"
                            "</attachment>"
                        ),
                    }
                )
        return parts

    async def read_file_bytes(
        self,
        attachment_id: str,
        *,
        tenant_ctx: TenantContext,
        thumbnail: bool = False,
    ) -> tuple[bytes, str, str]:
        row = await self.get_owned(attachment_id, tenant_ctx=tenant_ctx)
        if row is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
        path = row.thumbnail_path if thumbnail and row.thumbnail_path else row.storage_path
        mime = "image/webp" if thumbnail and row.thumbnail_path else row.mime_type
        data = await self.storage.download(path)
        return data, mime, row.original_filename

    def _to_response(self, row: ChatAttachment) -> ChatAttachmentResponse:
        return ChatAttachmentResponse(
            id=row.id,
            kind=row.kind,  # type: ignore[arg-type]
            originalFilename=row.original_filename,
            mimeType=row.mime_type,
            sizeBytes=row.size_bytes,
            width=row.width,
            height=row.height,
            thumbnailUrl=f"/api/agent/attachments/{row.id}/thumbnail" if row.thumbnail_path else None,
            url=f"/api/agent/attachments/{row.id}",
            createdAt=row.created_at,
        )

    @staticmethod
    async def _read_limited(file: UploadFile, max_bytes: int) -> bytes:
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = await file.read(64 * 1024)
            if not chunk:
                break
            total += len(chunk)
            if total > max_bytes:
                raise HTTPException(
                    status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                    detail=f"File exceeds {max_bytes} bytes",
                )
            chunks.append(chunk)
        if total == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty file",
            )
        return b"".join(chunks)

    @staticmethod
    def _detect_mime(content: bytes) -> str:
        detected = magic.Magic(mime=True).from_buffer(content[:8192])
        return detected or "application/octet-stream"

    @staticmethod
    def _verify_image(content: bytes) -> None:
        try:
            with Image.open(io.BytesIO(content)) as img:
                img.verify()
        except Image.DecompressionBombError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image dimensions exceed safe limits",
            ) from exc
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid image file",
            ) from exc
