"""Chat attachment upload / download endpoints."""

from typing import Annotated
from urllib.parse import quote

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.limiter import rate_limit
from app.modules.agent.dependencies import AgentTenantContext
from app.modules.agent.schemas_attachments import ChatAttachmentResponse
from app.modules.agent.services.chat_attachment_service import ChatAttachmentService
from app.modules.auth.dependencies import CurrentUser

router = APIRouter(prefix="/attachments", tags=["agent-attachments"])


def _get_service(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ChatAttachmentService:
    return ChatAttachmentService(db)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=ChatAttachmentResponse)
@rate_limit(settings.attachments.upload_rate_limit)
async def upload_attachment(
    request: Request,
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[ChatAttachmentService, Depends(_get_service)],
    file: UploadFile = File(...),
    sessionId: str | None = Form(default=None),
) -> ChatAttachmentResponse:
    """Upload a chat attachment (images in stages 1–3)."""
    _ = request
    _ = current_user
    return await service.upload_image(
        tenant_ctx=tenant_ctx,
        file=file,
        session_id=sessionId,
    )


@router.get("/{attachment_id}")
async def get_attachment(
    attachment_id: str,
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[ChatAttachmentService, Depends(_get_service)],
) -> Response:
    _ = current_user
    data, mime, filename = await service.read_file_bytes(
        attachment_id,
        tenant_ctx=tenant_ctx,
        thumbnail=False,
    )
    safe_name = quote(filename.replace('"', ""))
    return Response(
        content=data,
        media_type=mime,
        headers={
            "Content-Disposition": f'inline; filename="{safe_name}"',
            "Cache-Control": "private, max-age=3600",
        },
    )


@router.get("/{attachment_id}/thumbnail")
async def get_attachment_thumbnail(
    attachment_id: str,
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[ChatAttachmentService, Depends(_get_service)],
) -> Response:
    _ = current_user
    data, mime, filename = await service.read_file_bytes(
        attachment_id,
        tenant_ctx=tenant_ctx,
        thumbnail=True,
    )
    safe_name = quote(filename.replace('"', ""))
    return Response(
        content=data,
        media_type=mime,
        headers={
            "Content-Disposition": f'inline; filename="{safe_name}"',
            "Cache-Control": "private, max-age=3600",
        },
    )


@router.delete("/{attachment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_attachment(
    attachment_id: str,
    current_user: CurrentUser,
    tenant_ctx: AgentTenantContext,
    service: Annotated[ChatAttachmentService, Depends(_get_service)],
) -> None:
    _ = current_user
    deleted = await service.delete_owned(attachment_id, tenant_ctx=tenant_ctx)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attachment not found")
