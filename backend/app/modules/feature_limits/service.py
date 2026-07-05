"""Service for feature limits operations."""

from app.modules.feature_limits.db_models import FeatureLimitDB
from app.modules.feature_limits.repository import FeatureLimitRepository
from app.modules.feature_limits.schemas import (
    FeatureLimitCreate,
    FeatureLimitResponse,
    FeatureLimitUpdate,
)


class FeatureLimitService:
    """Service for feature limits operations."""

    def __init__(self, repo: FeatureLimitRepository):
        """Initialize service.

        Args:
            repo: Feature limit repository
        """
        self.repo = repo

    async def get_by_role(self, role: str) -> FeatureLimitResponse | None:
        """Get limit by role.

        Args:
            role: User role

        Returns:
            Limit response or None if not found
        """
        limit = await self.repo.get_by_role(role)
        if not limit:
            return None
        return FeatureLimitResponse.from_db(limit)

    async def get_all(self) -> list[FeatureLimitResponse]:
        """Get all limits.

        Returns:
            List of all limits
        """
        limits = await self.repo.get_all()
        return [FeatureLimitResponse.from_db(limit) for limit in limits]

    async def create(self, data: FeatureLimitCreate) -> FeatureLimitResponse:
        """Create new limit.

        Args:
            data: Limit data

        Returns:
            Created limit
        """
        limit = await self.repo.create(**data.model_dump())
        return FeatureLimitResponse.from_db(limit)

    async def update(self, role: str, data: FeatureLimitUpdate) -> FeatureLimitResponse:
        """Update limit.

        Args:
            role: User role
            data: Update data

        Returns:
            Updated limit
        """
        limit = await self.repo.get_by_role(role)
        if not limit:
            raise ValueError(f"Limit for role '{role}' not found")

        update_dict = data.model_dump(exclude_none=True)
        updated = await self.repo.update(limit, **update_dict)
        return FeatureLimitResponse.from_db(updated)

    async def delete(self, role: str) -> None:
        """Delete limit.

        Args:
            role: User role
        """
        limit = await self.repo.get_by_role(role)
        if not limit:
            raise ValueError(f"Limit for role '{role}' not found")

        await self.repo.delete(limit)
