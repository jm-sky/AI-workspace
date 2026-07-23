"""Tests for chat attachment validation helpers."""

import io

import pytest
from fastapi import HTTPException
from PIL import Image

from app.modules.agent.services.chat_attachment_service import (
    ALLOWED_MIME_TYPES,
    REJECTED_MIME_TYPES,
    ChatAttachmentService,
)


def _png_bytes(width: int = 8, height: int = 8) -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (width, height), color=(20, 40, 60)).save(buf, format="PNG")
    return buf.getvalue()


def test_detect_mime_png():
    mime = ChatAttachmentService._detect_mime(_png_bytes())
    assert mime == "image/png"
    assert mime in ALLOWED_MIME_TYPES


def test_svg_rejected_from_allow_list():
    assert "image/svg+xml" in REJECTED_MIME_TYPES
    assert "image/svg+xml" not in ALLOWED_MIME_TYPES


def test_verify_image_accepts_png():
    ChatAttachmentService._verify_image(_png_bytes())


def test_verify_image_rejects_garbage():
    with pytest.raises(HTTPException) as exc:
        ChatAttachmentService._verify_image(b"not-an-image")
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_read_limited_rejects_oversized(monkeypatch):
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
