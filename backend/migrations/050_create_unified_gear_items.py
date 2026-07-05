"""Migration: Create unified gear_items_v2 table.

This migration creates the unified gear_items_v2 table where containers become items
with item_type='container'. This is the first step of the unified model migration.

The unified model:
- Combines gear_containers and gear_items into a single table
- Uses item_type discriminator ('container' | 'item')
- Unifies nesting: parent_item_id replaces parent_container_id + container_id
- Removes nested_container_id (legacy, unused in API)
- Renames 'order' to 'order_index' (SQL keyword avoidance)

Benefits:
- O(1) lookups via flat Map structure
- Arbitrary nesting depth
- Simpler schema and reduced joins
- Foundation for future features (tags, custom fields)

Usage:
    python migrations/041_create_unified_gear_items.py upgrade
    python migrations/041_create_unified_gear_items.py downgrade
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import engine


async def table_exists(conn, table_name: str) -> bool:
    """Check if a table exists in the database."""
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = :table_name
            );
        """
        ),
        {"table_name": table_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Create unified gear_items_v2 table."""
    print("Creating unified gear_items_v2 table...")

    async with engine.begin() as conn:
        items_v2_exist = await table_exists(conn, "gear_items_v2")
        if not items_v2_exist:
            print("Creating gear_items_v2 table...")
            await conn.execute(
                text(
                    """
                    CREATE TABLE gear_items_v2 (
                        -- Identity
                        id VARCHAR(36) PRIMARY KEY,
                        user_id VARCHAR(36) NOT NULL,

                        -- TYPE DISCRIMINATOR (NEW!)
                        item_type VARCHAR(20) NOT NULL DEFAULT 'item'
                            CHECK (item_type IN ('container', 'item')),

                        -- UNIFIED NESTING (replaces parent_container_id + container_id + nested_container_id)
                        parent_item_id VARCHAR(36),

                        -- Common fields (from both models)
                        name VARCHAR(255) NOT NULL,
                        description TEXT,
                        brand VARCHAR(255),
                        price FLOAT,
                        currency VARCHAR(10),
                        weight FLOAT,
                        weight_unit VARCHAR(5),
                        url TEXT,
                        color VARCHAR(50),
                        notes TEXT,

                        -- Container-specific (nullable for items)
                        container_type VARCHAR(50),
                        max_weight FLOAT,
                        max_weight_unit VARCHAR(5),
                        hide_when_nested BOOLEAN DEFAULT FALSE,
                        is_public BOOLEAN DEFAULT FALSE,
                        favorite BOOLEAN DEFAULT FALSE,
                        show_item_images BOOLEAN DEFAULT FALSE,

                        -- Item-specific (nullable for containers)
                        category VARCHAR(50),
                        quantity INTEGER DEFAULT 1,
                        status VARCHAR(20) DEFAULT 'owned',
                        priority VARCHAR(20) DEFAULT 'medium',
                        expiration_date TIMESTAMP WITH TIME ZONE,
                        quality VARCHAR(20),
                        wearable BOOLEAN DEFAULT FALSE,
                        consumable BOOLEAN DEFAULT FALSE,
                        order_index INTEGER,
                        show_on_container BOOLEAN DEFAULT FALSE,

                        -- Linking (preserved)
                        linked_item_id VARCHAR(36),
                        catalogue_item_id VARCHAR(36),

                        -- Metadata
                        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),
                        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT (NOW() AT TIME ZONE 'UTC'),

                        -- Foreign keys
                        CONSTRAINT fk_gear_items_v2_user
                            FOREIGN KEY (user_id)
                            REFERENCES users(id)
                            ON DELETE CASCADE,
                        CONSTRAINT fk_gear_items_v2_parent
                            FOREIGN KEY (parent_item_id)
                            REFERENCES gear_items_v2(id)
                            ON DELETE CASCADE,
                        CONSTRAINT fk_gear_items_v2_linked_item
                            FOREIGN KEY (linked_item_id)
                            REFERENCES gear_items_v2(id)
                            ON DELETE SET NULL,
                        CONSTRAINT fk_gear_items_v2_catalogue_item
                            FOREIGN KEY (catalogue_item_id)
                            REFERENCES global_catalogue_items(id)
                            ON DELETE SET NULL,

                        -- Type-specific fields validation
                        CONSTRAINT check_container_fields CHECK (
                            item_type != 'container' OR (
                                category IS NULL AND
                                quantity IS NULL AND
                                status IS NULL AND
                                priority IS NULL AND
                                expiration_date IS NULL AND
                                wearable IS NULL AND
                                consumable IS NULL AND
                                order_index IS NULL AND
                                show_on_container IS NULL
                            )
                        ),
                        CONSTRAINT check_item_fields CHECK (
                            item_type != 'item' OR (
                                container_type IS NULL AND
                                max_weight IS NULL AND
                                max_weight_unit IS NULL AND
                                hide_when_nested IS NULL AND
                                is_public IS NULL AND
                                favorite IS NULL AND
                                show_item_images IS NULL
                            )
                        )
                    );
                """
                )
            )
            print("✓ Created gear_items_v2 table")

            # Create indexes for performance
            print("Creating indexes...")

            await conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_gear_items_v2_user_id
                    ON gear_items_v2(user_id);
                """
                )
            )
            print("✓ Created index: idx_gear_items_v2_user_id")

            await conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_gear_items_v2_parent_item_id
                    ON gear_items_v2(parent_item_id);
                """
                )
            )
            print("✓ Created index: idx_gear_items_v2_parent_item_id")

            await conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_gear_items_v2_item_type
                    ON gear_items_v2(item_type);
                """
                )
            )
            print("✓ Created index: idx_gear_items_v2_item_type")

            await conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_gear_items_v2_is_public
                    ON gear_items_v2(is_public)
                    WHERE item_type = 'container';
                """
                )
            )
            print("✓ Created index: idx_gear_items_v2_is_public")

            await conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_gear_items_v2_linked_item_id
                    ON gear_items_v2(linked_item_id);
                """
                )
            )
            print("✓ Created index: idx_gear_items_v2_linked_item_id")

            await conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_gear_items_v2_catalogue_item_id
                    ON gear_items_v2(catalogue_item_id);
                """
                )
            )
            print("✓ Created index: idx_gear_items_v2_catalogue_item_id")

            await conn.execute(
                text(
                    """
                    CREATE INDEX IF NOT EXISTS idx_gear_items_v2_favorite
                    ON gear_items_v2(favorite)
                    WHERE item_type = 'container';
                """
                )
            )
            print("✓ Created index: idx_gear_items_v2_favorite")

            print("✓ All indexes created successfully")
        else:
            print("✓ gear_items_v2 table already exists")


async def downgrade() -> None:
    """Drop unified gear_items_v2 table."""
    print("Dropping gear_items_v2 table...")

    async with engine.begin() as conn:
        items_v2_exist = await table_exists(conn, "gear_items_v2")
        if items_v2_exist:
            print("Dropping gear_items_v2 table...")
            await conn.execute(
                text(
                    """
                    DROP TABLE IF EXISTS gear_items_v2 CASCADE;
                """
                )
            )
            print("✓ Dropped gear_items_v2 table")
        else:
            print("✓ gear_items_v2 table does not exist")


async def main() -> None:
    """Run migration based on command line argument."""
    if len(sys.argv) < 2:
        print(
            "Usage: python migrations/041_create_unified_gear_items.py [upgrade|downgrade]"
        )
        sys.exit(1)

    command = sys.argv[1].lower()
    if command == "upgrade":
        await upgrade()
    elif command == "downgrade":
        await downgrade()
    else:
        print(f"Unknown command: {command}")
        print(
            "Usage: python migrations/041_create_unified_gear_items.py [upgrade|downgrade]"
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
