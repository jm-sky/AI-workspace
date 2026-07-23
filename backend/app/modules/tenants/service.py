"""Tenant workspace context and switching."""

from dataclasses import dataclass

from fastapi import Depends, HTTPException, status

from app.core.config import settings
from app.modules.auth.auth_utils import (
    create_access_token,
    create_refresh_token,
    verify_token,
)
from app.modules.auth.dependencies import CurrentUser, get_current_token
from app.modules.auth.models import User
from app.modules.auth.repositories import UserRepository, get_user_repository
from app.modules.auth.types.jwt import CreateAccessTokenOptions, CreateRefreshTokenOptions
from app.modules.teams.repositories import TeamRepository, get_team_repository
from app.modules.tenants.repositories import TenantRepository, get_tenant_repository


@dataclass(frozen=True)
class TenantContext:
    """Resolved active tenant/team context for the current request."""

    user_id: str
    tenant_id: str
    tenant_role: str
    team_id: str | None = None


class TenantWorkspaceService:
    """Business logic for tenant/team workspace switching."""

    def __init__(
        self,
        tenant_repo: TenantRepository,
        team_repo: TeamRepository,
        user_repo: UserRepository,
    ):
        self.tenant_repo = tenant_repo
        self.team_repo = team_repo
        self.user_repo = user_repo

    async def resolve_workspace_for_user(self, user: User) -> TenantContext | None:
        tenant_id = user.activeTenantId
        team_id = user.activeTeamId

        if tenant_id:
            membership = await self.tenant_repo.get_membership(tenant_id, user.id)
            if membership:
                if team_id:
                    team = await self.team_repo.get_team(team_id)
                    team_membership = await self.team_repo.get_membership(team_id, user.id)
                    if team is None or team.tenant_id != tenant_id or team_membership is None:
                        team_id = None
                return TenantContext(
                    user_id=user.id,
                    tenant_id=tenant_id,
                    tenant_role=membership.role,
                    team_id=team_id,
                )

        tenants = await self.tenant_repo.list_for_user(user.id)
        if len(tenants) == 1:
            tenant, membership = tenants[0]
            if not user.activeTenantId:
                await self.user_repo.set_active_workspace(user.id, tenant.id, None)
            return TenantContext(
                user_id=user.id,
                tenant_id=tenant.id,
                tenant_role=membership.role,
                team_id=None,
            )

        return None

    async def ensure_personal_workspace(
        self,
        user: User,
        *,
        workspace_name: str | None = None,
    ) -> TenantContext | None:
        """Create a personal workspace when the user has none."""
        tenants = await self.tenant_repo.list_for_user(user.id)
        if tenants:
            return await self.resolve_workspace_for_user(user)

        name = (workspace_name or f"{user.name}'s Workspace").strip() or "My Workspace"
        if len(name) > 255:
            name = name[:255]

        tenant, membership = await self.tenant_repo.create_tenant(
            name=name,
            description=None,
            owner_user_id=user.id,
        )
        from app.modules.agent.services.agent_definition_service import AgentDefinitionService

        await AgentDefinitionService(self.tenant_repo.db).seed_builtins_for_tenant(
            tenant.id,
            created_by=user.id,
        )
        await self.user_repo.set_active_workspace(user.id, tenant.id, None)
        return TenantContext(
            user_id=user.id,
            tenant_id=tenant.id,
            tenant_role=membership.role,
            team_id=None,
        )

    async def switch_workspace(
        self,
        *,
        user: User,
        tenant_id: str,
        team_id: str | None,
        session_jti: str | None = None,
        tfa_verified: bool = False,
        tfa_method: str | None = None,
    ) -> dict[str, str | int]:
        membership = await self.tenant_repo.get_membership(tenant_id, user.id)
        if membership is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not a member of this tenant",
            )

        if team_id:
            team = await self.team_repo.get_team(team_id)
            if team is None or team.tenant_id != tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Team does not belong to this tenant",
                )
            team_membership = await self.team_repo.get_membership(team_id, user.id)
            if team_membership is None:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not a member of this team",
                )

        updated_user = await self.user_repo.set_active_workspace(user.id, tenant_id, team_id)

        token_data: CreateAccessTokenOptions = {
            "sub": updated_user.id,
            "email": updated_user.email,
            "tfaVerified": tfa_verified,
            "tfaMethod": tfa_method,
            "emailVerified": updated_user.isEmailVerified,
            "tid": tenant_id,
            "trol": membership.role,
            "tv": updated_user.tokenVersion,
        }
        if team_id:
            token_data["tmid"] = team_id
        if session_jti:
            token_data["jti"] = session_jti

        access_token = create_access_token(data=token_data)
        refresh_data: CreateRefreshTokenOptions = {
            "sub": updated_user.id,
            "email": updated_user.email,
            "tfaVerified": tfa_verified,
            "tfaMethod": tfa_method,
            "emailVerified": updated_user.isEmailVerified,
            "tv": updated_user.tokenVersion,
        }
        if session_jti:
            refresh_data["jti"] = session_jti
        refresh_token = create_refresh_token(data=refresh_data)

        return {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "tokenType": "bearer",
            "expiresIn": settings.security.access_token_expires_minutes * 60,
        }

    def workspace_claims(self, workspace: TenantContext | None) -> CreateAccessTokenOptions:
        if workspace is None:
            return {}
        claims: CreateAccessTokenOptions = {
            "tid": workspace.tenant_id,
            "trol": workspace.tenant_role,
        }
        if workspace.team_id:
            claims["tmid"] = workspace.team_id
        return claims


def get_tenant_workspace_service(
    tenant_repo: TenantRepository = Depends(get_tenant_repository),
    team_repo: TeamRepository = Depends(get_team_repository),
    user_repo: UserRepository = Depends(get_user_repository),
) -> TenantWorkspaceService:
    return TenantWorkspaceService(tenant_repo, team_repo, user_repo)


async def get_current_tenant_context(
    current_user: CurrentUser,
    token: str = Depends(get_current_token),
    tenant_repo: TenantRepository = Depends(get_tenant_repository),
    team_repo: TeamRepository = Depends(get_team_repository),
) -> TenantContext:
    try:
        payload = verify_token(token)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from exc

    tenant_id = payload.get("tid")
    tenant_role = payload.get("trol")
    if not tenant_id or not tenant_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No active tenant in token — call POST /tenants/switch first",
        )

    membership = await tenant_repo.get_membership(tenant_id, current_user.id)
    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not a member of active tenant",
        )

    team_id = payload.get("tmid")
    if team_id:
        team = await team_repo.get_team(team_id)
        team_membership = await team_repo.get_membership(team_id, current_user.id)
        if team is None or team.tenant_id != tenant_id or team_membership is None:
            team_id = None

    return TenantContext(
        user_id=current_user.id,
        tenant_id=tenant_id,
        tenant_role=membership.role,
        team_id=team_id,
    )


CurrentTenantContext = TenantContext  # type alias for Annotated usage
