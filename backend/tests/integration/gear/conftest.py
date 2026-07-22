"""Pytest fixtures for gear module integration tests.

PHASE 0: Test Creation (Pre-Implementation Safety Net)
These fixtures establish baseline behavior before unified model migration.
"""

import os
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

import pytest
import pytest_asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base
from app.modules.auth.auth_utils import get_password_hash
from app.modules.auth.db_models import UserDB
from app.modules.gear.db_models import GearContainerDB, GearItemDB
from app.modules.gear.repository import GearRepository
from app.modules.gear.repository_v2 import GearRepositoryV2
from app.modules.gear.schemas import ContainerCreate, ItemCreate
from app.modules.gear.service import GearService
from app.modules.gear.service_v2 import GearServiceV2


@pytest_asyncio.fixture
async def async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Create async database session for testing.

    Uses PostgreSQL test database (backend_test) from Docker container.
    Creates and drops all tables for each test to ensure isolation.
    """
    # Use PostgreSQL test database from Docker
    # Connection from within Docker: db:5432
    # Connection from host: localhost:5432 (if running tests outside Docker)
    db_password = os.getenv("POSTGRES_PASSWORD", "changeme")
    test_db_url = f"postgresql+asyncpg://backend:{db_password}@db:5432/backend_test"

    engine = create_async_engine(
        test_db_url,
        echo=False,  # Set to True for SQL query debugging
    )

    # Create all tables before test
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Create session
    async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        yield session

    # Drop all tables after test for isolation
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture
async def test_user(async_db_session: AsyncSession) -> UserDB:
    """Create a test user in the database."""
    user = UserDB(
        id="test-user-id-123",
        email="test@example.com",
        name="Test User",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        is_email_verified=True,
        created_at=datetime.now(UTC),
    )

    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def gear_repository(async_db_session: AsyncSession) -> GearRepository:
    """Create gear repository instance."""
    return GearRepository(async_db_session)


@pytest_asyncio.fixture
async def gear_service(gear_repository: GearRepository) -> GearService:
    """Create gear service instance."""
    return GearService(gear_repository)


@pytest_asyncio.fixture
async def gear_repository_v2(async_db_session: AsyncSession) -> GearRepositoryV2:
    """Create gear repository V2 instance."""
    return GearRepositoryV2(async_db_session)


@pytest_asyncio.fixture
async def gear_service_v2(gear_repository_v2: GearRepositoryV2) -> GearServiceV2:
    """Create gear service V2 instance."""
    return GearServiceV2(gear_repository_v2)


@pytest.fixture
def sample_container_data() -> ContainerCreate:
    """Create sample container data for testing."""
    return ContainerCreate(
        name="Test Backpack",
        description="A test backpack for integration tests",
        type="backpack",
        color="coyote",
        weight=500.0,
        weightUnit="g",
        brand="TestBrand",
        price=99.99,
    )


@pytest.fixture
def sample_item_data() -> ItemCreate:
    """Create sample item data for testing."""
    return ItemCreate(
        name="Water Bottle",
        category="water",
        quantity=1,
        weight=300.0,
        weight_unit="g",
        priority="high",
        status="owned",
        brand="Nalgene",
        price=15.99,
        currency="USD",
    )


async def create_test_container(
    service: GearService,
    user_id: str,
    name: str = "Test Container",
    container_type: str = "backpack",
    parent_id: str | None = None,
    weight: float | None = None,
    weight_unit: str | None = "g",
) -> dict:
    """Helper function to create a test container.

    Args:
        service: Gear service instance
        user_id: User ID
        name: Container name
        container_type: Container type
        parent_id: Parent container ID for nesting
        weight: Container weight
        weight_unit: Weight unit

    Returns:
        Created container as dict
    """
    data = ContainerCreate(
        name=name,
        type=container_type,
        parentContainerId=parent_id,
        weight=weight,
        weightUnit=weight_unit,
    )
    container = await service.create_container(user_id, data)
    return container.model_dump()


async def create_test_item(
    service: GearService,
    user_id: str,
    container_id: str,
    name: str = "Test Item",
    category: str = "tools",
    quantity: int = 1,
    weight: float = 100.0,
    weight_unit: str = "g",
    status: str = "owned",
    priority: str = "medium",
) -> dict:
    """Helper function to create a test item.

    Args:
        service: Gear service instance
        user_id: User ID
        container_id: Container ID
        name: Item name
        category: Item category
        quantity: Item quantity
        weight: Item weight
        weight_unit: Weight unit
        status: Item status
        priority: Item priority

    Returns:
        Created item as dict
    """
    data = ItemCreate(
        name=name,
        category=category,
        quantity=quantity,
        weight=weight,
        weightUnit=weight_unit,
        status=status,
        priority=priority,
    )
    item = await service.create_item(container_id, user_id, data)
    return item.model_dump()


async def get_container_count(session: AsyncSession, user_id: str) -> int:
    """Get total number of containers for a user."""
    result = await session.execute(select(GearContainerDB).where(GearContainerDB.user_id == user_id))
    containers = result.scalars().all()
    return len(containers)


async def get_item_count(session: AsyncSession, container_id: str) -> int:
    """Get total number of items in a container."""
    result = await session.execute(select(GearItemDB).where(GearItemDB.container_id == container_id))
    items = result.scalars().all()
    return len(items)
