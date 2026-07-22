"""Repository for team operations."""

import logging

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.id_utils import generate_id
from app.core.database import get_db
from app.modules.teams.db_models import TeamDB, TeamMembershipDB

logger = logging.getLogger(__name__)


class TeamRepository:
    """Data access layer for teams and memberships."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_for_user_in_tenant(self, *, user_id: str, tenant_id: str) -> list[tuple[TeamDB, TeamMembershipDB]]:
        stmt = (
            select(TeamDB, TeamMembershipDB)
            .join(TeamMembershipDB, TeamMembershipDB.team_id == TeamDB.id)
            .where(
                TeamMembershipDB.user_id == user_id,
                TeamDB.tenant_id == tenant_id,
            )
            .order_by(TeamDB.created_at)
        )
        result = await self.db.execute(stmt)
        return [(row[0], row[1]) for row in result.all()]

    async def list_for_tenant(self, tenant_id: str) -> list[TeamDB]:
        stmt = select(TeamDB).where(TeamDB.tenant_id == tenant_id).order_by(TeamDB.created_at)
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_team(self, team_id: str) -> TeamDB | None:
        result = await self.db.execute(select(TeamDB).where(TeamDB.id == team_id))
        return result.scalar_one_or_none()

    async def get_membership(self, team_id: str, user_id: str) -> TeamMembershipDB | None:
        result = await self.db.execute(
            select(TeamMembershipDB).where(
                TeamMembershipDB.team_id == team_id,
                TeamMembershipDB.user_id == user_id,
            )
        )
        return result.scalar_one_or_none()

    async def create_team(
        self,
        *,
        tenant_id: str,
        name: str,
        description: str | None,
        creator_user_id: str,
    ) -> tuple[TeamDB, TeamMembershipDB]:
        team_id = generate_id()
        team = TeamDB(
            id=team_id,
            tenant_id=tenant_id,
            name=name,
            description=description,
        )
        membership = TeamMembershipDB(
            team_id=team_id,
            user_id=creator_user_id,
            role="owner",
        )
        self.db.add(team)
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(team)
        return team, membership

    async def add_member(self, team_id: str, user_id: str, role: str = "member") -> TeamMembershipDB:
        existing = await self.get_membership(team_id, user_id)
        if existing:
            logger.info("User %s already member of team %s", user_id, team_id)
            return existing

        membership = TeamMembershipDB(
            team_id=team_id,
            user_id=user_id,
            role=role,
        )
        self.db.add(membership)
        await self.db.commit()
        await self.db.refresh(membership)
        return membership


def get_team_repository(db: AsyncSession = Depends(get_db)) -> TeamRepository:
    return TeamRepository(db)
