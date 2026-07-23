"""Tests for chat attachment validation helpers."""

import io

import pytest
from fastapi import HTTPException
from PIL import Image
from pypdf import PdfWriter

from app.modules.agent.services.chat_attachment_service import (
    ALLOWED_MIME_TYPES,
    PDF_MIME_TYPES,
    REJECTED_MIME_TYPES,
    TEXT_MIME_TYPES,
    ChatAttachmentService,
)


def _png_bytes(width: int = 8, height: int = 8) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=(20, 40, 60)).save(buf, format="PNG")
    return buf.getvalue()


def _blank_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=200, height=200)
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def test_detect_mime_png():
    mime = ChatAttachmentService._detect_mime(_png_bytes())
    assert mime == "image/png"
    assert mime in ALLOWED_MIME_TYPES


def test_allow_lists_include_text_and_pdf():
    assert "text/plain" in TEXT_MIME_TYPES
    assert "application/json" in TEXT_MIME_TYPES
    assert "application/pdf" in PDF_MIME_TYPES
    assert "application/pdf" in ALLOWED_MIME_TYPES


def test_svg_rejected_from_allow_list():
    assert "image/svg+xml" in REJECTED_MIME_TYPES
    assert "image/svg+xml" not in ALLOWED_MIME_TYPES


def test_verify_image_accepts_png():
    ChatAttachmentService._verify_image(_png_bytes())


def test_verify_image_rejects_garbage():
    with pytest.raises(HTTPException) as exc:
        ChatAttachmentService._verify_image(b"not-an-image")
    assert exc.value.status_code == 400


def test_extract_plain_text_utf8_bom():
    service = ChatAttachmentService.__new__(ChatAttachmentService)
    content = "\ufeffhello\nworld".encode("utf-8-sig")
    text, chars = service._extract_plain_text(content)
    assert text.startswith("hello")
    assert chars == len(text)


def test_extract_plain_text_rejects_null_bytes():
    service = ChatAttachmentService.__new__(ChatAttachmentService)
    with pytest.raises(HTTPException) as exc:
        service._extract_plain_text(b"abc\x00def")
    assert exc.value.status_code == 400


def test_extract_pdf_invalid():
    service = ChatAttachmentService.__new__(ChatAttachmentService)
    service._cfg = type("Cfg", (), {"pdf_max_pages": 50})()
    with pytest.raises(HTTPException) as exc:
        service._extract_pdf_text(b"not-a-pdf")
    assert exc.value.status_code == 400


def test_extract_pdf_blank_has_no_text():
    service = ChatAttachmentService.__new__(ChatAttachmentService)
    service._cfg = type("Cfg", (), {"pdf_max_pages": 50})()
    with pytest.raises(HTTPException) as exc:
        service._extract_pdf_text(_blank_pdf_bytes())
    assert exc.value.status_code == 400
    assert "text" in str(exc.value.detail).lower()


@pytest.mark.asyncio
async def test_read_limited_rejects_oversized():
    class FakeUpload:
        def __init__(self, payload: bytes):
            self._payload = payload
            self._offset = 0

        async def read(self, n: int = -1) -> bytes:
            if self._offset >= len(self._payload):
                return b""
            end = len(self._payload) if n < 0 else min(self._offset + n, len(self._payload))
            chunk = self._payload[self._offset:end]
            self._offset = end
            return chunk

    big = b"x" * 100
    with pytest.raises(HTTPException) as exc:
        await ChatAttachmentService._read_limited(FakeUpload(big), max_bytes=50)
    assert exc.value.status_code == 413


@pytest.mark.asyncio
async def test_purge_orphans_dry_run_does_not_delete():
    from datetime import UTC, datetime, timedelta
    from unittest.mock import AsyncMock, MagicMock

    old = MagicMock()
    old.run_id = None
    old.storage_path = "a/path"
    old.thumbnail_path = None
    old.created_at = datetime.now(UTC) - timedelta(hours=48)

    result = MagicMock()
    result.scalars.return_value.all.return_value = [old]

    db = AsyncMock()
    db.execute = AsyncMock(return_value=result)
    db.delete = AsyncMock()
    db.commit = AsyncMock()

    storage = AsyncMock()
    service = ChatAttachmentService.__new__(ChatAttachmentService)
    service.db = db
    service.storage = storage
    service._cfg = type("Cfg", (), {"orphan_ttl_hours": 24})()

    count = await service.purge_orphans(dry_run=True)
    assert count == 1
    storage.delete.assert_not_called()
    db.delete.assert_not_called()


@pytest.mark.asyncio
async def test_purge_orphans_deletes_storage_and_rows():
    from datetime import UTC, datetime, timedelta
    from unittest.mock import AsyncMock, MagicMock

    orphan = MagicMock()
    orphan.run_id = None
    orphan.storage_path = "chat/a.bin"
    orphan.thumbnail_path = "chat/a.thumb"
    orphan.created_at = datetime.now(UTC) - timedelta(hours=48)

    result = MagicMock()
    result.scalars.return_value.all.return_value = [orphan]

    db = AsyncMock()
    db.execute = AsyncMock(return_value=result)
    db.delete = AsyncMock()
    db.commit = AsyncMock()

    storage = AsyncMock()
    service = ChatAttachmentService.__new__(ChatAttachmentService)
    service.db = db
    service.storage = storage
    service._cfg = type("Cfg", (), {"orphan_ttl_hours": 24})()

    count = await service.purge_orphans()
    assert count == 1
    assert storage.delete.await_count == 2
    db.delete.assert_awaited_once_with(orphan)
    db.commit.assert_awaited()
