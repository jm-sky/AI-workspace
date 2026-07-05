"""Migration: Update foreign keys to point to gear_items_v2.

This migration updates foreign keys in related tables to point to the unified
gear_items_v2 table instead of the old gear_containers and gear_items tables.

Tables updated:
- item_images: item_id FK → gear_items_v2
- container_share_tokens: container_id FK → gear_items_v2
- container_ratings: container_id FK → gear_items_v2

This is necessary because the unified model combines containers and items into
a single table, so all foreign keys need to be updated accordingly.

Usage:
    python migrations/043_update_foreign_keys_to_unified_model.py upgrade
    python migrations/043_update_foreign_keys_to_unified_model.py downgrade
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


async def constraint_exists(conn, table_name: str, constraint_name: str) -> bool:
    """Check if a constraint exists on a table."""
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.table_constraints
                WHERE table_schema = 'public'
                AND table_name = :table_name
                AND constraint_name = :constraint_name
            );
        """
        ),
        {"table_name": table_name, "constraint_name": constraint_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Update foreign keys to point to gear_items_v2."""
    print("Updating foreign keys to gear_items_v2...")

    async with engine.begin() as conn:
        # Verify gear_items_v2 exists
        items_v2_exist = await table_exists(conn, "gear_items_v2")
        if not items_v2_exist:
            print(
                "❌ Error: gear_items_v2 table does not exist. Run migrations 041 and 042 first."
            )
            sys.exit(1)

        # 1. Update item_images table
        print("Step 1: Updating item_images foreign key...")
        item_images_exist = await table_exists(conn, "item_images")
        if item_images_exist:
            # Drop old constraint if exists
            old_constraint = await constraint_exists(
                conn, "item_images", "item_images_item_id_fkey"
            )
            if old_constraint:
                await conn.execute(
                    text(
                        """
                        ALTER TABLE item_images
                        DROP CONSTRAINT IF EXISTS item_images_item_id_fkey;
                    """
                    )
                )
                print("  ✓ Dropped old constraint: item_images_item_id_fkey")

            # Add new constraint pointing to gear_items_v2
            await conn.execute(
                text(
                    """
                    ALTER TABLE item_images
                    ADD CONSTRAINT item_images_item_id_fkey
                        FOREIGN KEY (item_id)
                        REFERENCES gear_items_v2(id)
                        ON DELETE CASCADE;
                """
                )
            )
            print("  ✓ Added new constraint: item_images → gear_items_v2")
        else:
            print("  ⚠️  item_images table does not exist, skipping")

        # 2. Update container_share_tokens table
        print("Step 2: Updating container_share_tokens foreign key...")
        share_tokens_exist = await table_exists(conn, "container_share_tokens")
        if share_tokens_exist:
            # Drop old constraint if exists
            old_constraint = await constraint_exists(
                conn,
                "container_share_tokens",
                "container_share_tokens_container_id_fkey",
            )
            if old_constraint:
                await conn.execute(
                    text(
                        """
                        ALTER TABLE container_share_tokens
                        DROP CONSTRAINT IF EXISTS container_share_tokens_container_id_fkey;
                    """
                    )
                )
                print(
                    "  ✓ Dropped old constraint: container_share_tokens_container_id_fkey"
                )

            # Add new constraint pointing to gear_items_v2
            await conn.execute(
                text(
                    """
                    ALTER TABLE container_share_tokens
                    ADD CONSTRAINT container_share_tokens_container_id_fkey
                        FOREIGN KEY (container_id)
                        REFERENCES gear_items_v2(id)
                        ON DELETE CASCADE;
                """
                )
            )
            print("  ✓ Added new constraint: container_share_tokens → gear_items_v2")
        else:
            print("  ⚠️  container_share_tokens table does not exist, skipping")

        # 3. Update container_ratings table
        print("Step 3: Updating container_ratings foreign key...")
        ratings_exist = await table_exists(conn, "container_ratings")
        if ratings_exist:
            # Drop old constraint if exists
            old_constraint = await constraint_exists(
                conn, "container_ratings", "container_ratings_container_id_fkey"
            )
            if old_constraint:
                await conn.execute(
                    text(
                        """
                        ALTER TABLE container_ratings
                        DROP CONSTRAINT IF EXISTS container_ratings_container_id_fkey;
                    """
                    )
                )
                print("  ✓ Dropped old constraint: container_ratings_container_id_fkey")

            # Add new constraint pointing to gear_items_v2
            await conn.execute(
                text(
                    """
                    ALTER TABLE container_ratings
                    ADD CONSTRAINT container_ratings_container_id_fkey
                        FOREIGN KEY (container_id)
                        REFERENCES gear_items_v2(id)
                        ON DELETE CASCADE;
                """
                )
            )
            print("  ✓ Added new constraint: container_ratings → gear_items_v2")
        else:
            print("  ⚠️  container_ratings table does not exist, skipping")

        print("✓ All foreign keys updated successfully!")


async def downgrade() -> None:
    """Revert foreign keys to point back to gear_items and gear_containers."""
    print("Reverting foreign keys to gear_items and gear_containers...")

    async with engine.begin() as conn:
        # 1. Revert item_images table
        print("Step 1: Reverting item_images foreign key...")
        item_images_exist = await table_exists(conn, "item_images")
        if item_images_exist:
            # Drop v2 constraint
            await conn.execute(
                text(
                    """
                    ALTER TABLE item_images
                    DROP CONSTRAINT IF EXISTS item_images_item_id_fkey;
                """
                )
            )
            print("  ✓ Dropped constraint: item_images_item_id_fkey")

            # Add back old constraint if gear_items exists
            items_exist = await table_exists(conn, "gear_items")
            if items_exist:
                await conn.execute(
                    text(
                        """
                        ALTER TABLE item_images
                        ADD CONSTRAINT item_images_item_id_fkey
                            FOREIGN KEY (item_id)
                            REFERENCES gear_items(id)
                            ON DELETE CASCADE;
                    """
                    )
                )
                print("  ✓ Restored constraint: item_images → gear_items")
        else:
            print("  ⚠️  item_images table does not exist, skipping")

        # 2. Revert container_share_tokens table
        print("Step 2: Reverting container_share_tokens foreign key...")
        share_tokens_exist = await table_exists(conn, "container_share_tokens")
        if share_tokens_exist:
            # Drop v2 constraint
            await conn.execute(
                text(
                    """
                    ALTER TABLE container_share_tokens
                    DROP CONSTRAINT IF EXISTS container_share_tokens_container_id_fkey;
                """
                )
            )
            print("  ✓ Dropped constraint: container_share_tokens_container_id_fkey")

            # Add back old constraint if gear_containers exists
            containers_exist = await table_exists(conn, "gear_containers")
            if containers_exist:
                await conn.execute(
                    text(
                        """
                        ALTER TABLE container_share_tokens
                        ADD CONSTRAINT container_share_tokens_container_id_fkey
                            FOREIGN KEY (container_id)
                            REFERENCES gear_containers(id)
                            ON DELETE CASCADE;
                    """
                    )
                )
                print(
                    "  ✓ Restored constraint: container_share_tokens → gear_containers"
                )
        else:
            print("  ⚠️  container_share_tokens table does not exist, skipping")

        # 3. Revert container_ratings table
        print("Step 3: Reverting container_ratings foreign key...")
        ratings_exist = await table_exists(conn, "container_ratings")
        if ratings_exist:
            # Drop v2 constraint
            await conn.execute(
                text(
                    """
                    ALTER TABLE container_ratings
                    DROP CONSTRAINT IF EXISTS container_ratings_container_id_fkey;
                """
                )
            )
            print("  ✓ Dropped constraint: container_ratings_container_id_fkey")

            # Add back old constraint if gear_containers exists
            containers_exist = await table_exists(conn, "gear_containers")
            if containers_exist:
                await conn.execute(
                    text(
                        """
                        ALTER TABLE container_ratings
                        ADD CONSTRAINT container_ratings_container_id_fkey
                            FOREIGN KEY (container_id)
                            REFERENCES gear_containers(id)
                            ON DELETE CASCADE;
                    """
                    )
                )
                print("  ✓ Restored constraint: container_ratings → gear_containers")
        else:
            print("  ⚠️  container_ratings table does not exist, skipping")

        print("✓ All foreign keys reverted successfully!")


async def main() -> None:
    """Run migration based on command line argument."""
    if len(sys.argv) < 2:
        print(
            "Usage: python migrations/043_update_foreign_keys_to_unified_model.py [upgrade|downgrade]"
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
            "Usage: python migrations/043_update_foreign_keys_to_unified_model.py [upgrade|downgrade]"
        )
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
