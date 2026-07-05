"""Migration: Add billing tables and migrate existing premium users.

Usage:
    python migrations/047_add_billing_tables.py upgrade
    python migrations/047_add_billing_tables.py downgrade
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text

from app.core.database import engine


async def table_exists(conn, table_name: str) -> bool:
    """Check if table exists (PostgreSQL compatible)."""
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


async def column_exists(conn, table_name: str, column_name: str) -> bool:
    """Check if column exists."""
    result = await conn.execute(
        text(
            """
            SELECT EXISTS (
                SELECT FROM information_schema.columns
                WHERE table_schema = 'public'
                AND table_name = :table_name
                AND column_name = :column_name
            );
        """
        ),
        {"table_name": table_name, "column_name": column_name},
    )
    return result.scalar() is True


async def upgrade() -> None:
    """Add billing tables and migrate existing premium users."""
    print("Adding billing support...")

    async with engine.begin() as conn:
        # 1. Create subscriptions table
        if not await table_exists(conn, "subscriptions"):
            await conn.execute(
                text(
                    """
                CREATE TABLE subscriptions (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    user_id VARCHAR(36) NOT NULL UNIQUE,
                    stripe_customer_id VARCHAR(255),
                    stripe_subscription_id VARCHAR(255) UNIQUE,
                    stripe_price_id VARCHAR(255),
                    plan_tier VARCHAR(20) NOT NULL DEFAULT 'free',
                    billing_interval VARCHAR(10),
                    status VARCHAR(20) NOT NULL DEFAULT 'active',
                    current_period_start TIMESTAMP WITH TIME ZONE,
                    current_period_end TIMESTAMP WITH TIME ZONE,
                    cancel_at_period_end BOOLEAN DEFAULT FALSE,
                    canceled_at TIMESTAMP WITH TIME ZONE,
                    is_grandfathered BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    CONSTRAINT fk_subscriptions_user
                        FOREIGN KEY (user_id)
                        REFERENCES users(id)
                        ON DELETE CASCADE,
                    CONSTRAINT valid_plan_tier
                        CHECK (plan_tier IN ('free', 'pro', 'pro_plus')),
                    CONSTRAINT valid_billing_interval
                        CHECK (billing_interval IN ('month', 'year')),
                    CONSTRAINT valid_status
                        CHECK (status IN ('active', 'canceled', 'past_due', 'unpaid', 'incomplete', 'trialing'))
                )
            """
                )
            )
            print("✓ Created subscriptions table")

            # Create indexes
            await conn.execute(
                text("CREATE INDEX idx_subscriptions_user_id ON subscriptions(user_id)")
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_subscriptions_stripe_customer_id ON subscriptions(stripe_customer_id)"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_subscriptions_stripe_subscription_id ON subscriptions(stripe_subscription_id)"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_subscriptions_plan_tier ON subscriptions(plan_tier)"
                )
            )
            await conn.execute(
                text("CREATE INDEX idx_subscriptions_status ON subscriptions(status)")
            )
            print("✓ Created indexes")

        # 2. Create stripe_webhook_events table
        if not await table_exists(conn, "stripe_webhook_events"):
            await conn.execute(
                text(
                    """
                CREATE TABLE stripe_webhook_events (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    stripe_event_id VARCHAR(255) NOT NULL UNIQUE,
                    event_type VARCHAR(100) NOT NULL,
                    payload JSONB NOT NULL,
                    processed BOOLEAN NOT NULL DEFAULT FALSE,
                    processed_at TIMESTAMP WITH TIME ZONE,
                    error_message TEXT,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
                )
            """
                )
            )
            print("✓ Created stripe_webhook_events table")

            # Create indexes
            await conn.execute(
                text(
                    "CREATE INDEX idx_webhook_events_event_id ON stripe_webhook_events(stripe_event_id)"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_webhook_events_processed ON stripe_webhook_events(processed)"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_webhook_events_event_type ON stripe_webhook_events(event_type)"
                )
            )
            print("✓ Created webhook event indexes")

        # 3. Create subscription_history table
        if not await table_exists(conn, "subscription_history"):
            await conn.execute(
                text(
                    """
                CREATE TABLE subscription_history (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    subscription_id UUID,
                    user_id VARCHAR(36) NOT NULL,
                    event_type VARCHAR(50) NOT NULL,
                    old_status VARCHAR(20),
                    new_status VARCHAR(20) NOT NULL,
                    old_plan_tier VARCHAR(20),
                    new_plan_tier VARCHAR(20) NOT NULL,
                    event_metadata JSONB,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
                    CONSTRAINT fk_subscription_history_subscription
                        FOREIGN KEY (subscription_id)
                        REFERENCES subscriptions(id)
                        ON DELETE CASCADE,
                    CONSTRAINT fk_subscription_history_user
                        FOREIGN KEY (user_id)
                        REFERENCES users(id)
                        ON DELETE CASCADE,
                    CONSTRAINT valid_event_type
                        CHECK (event_type IN ('created', 'updated', 'canceled', 'renewed', 'payment_failed'))
                )
            """
                )
            )
            print("✓ Created subscription_history table")

            # Create indexes
            await conn.execute(
                text(
                    "CREATE INDEX idx_subscription_history_subscription_id ON subscription_history(subscription_id)"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_subscription_history_user_id ON subscription_history(user_id)"
                )
            )
            await conn.execute(
                text(
                    "CREATE INDEX idx_subscription_history_event_type ON subscription_history(event_type)"
                )
            )
            print("✓ Created subscription history indexes")

        # 4. Migrate existing premium users to grandfathered Pro
        print("Migrating existing premium users...")
        await conn.execute(
            text(
                """
            INSERT INTO subscriptions (
                user_id, plan_tier, status, is_grandfathered, created_at, updated_at
            )
            SELECT
                id,
                'pro',
                'active',
                TRUE,
                created_at,
                NOW()
            FROM users
            WHERE is_premium = TRUE
            ON CONFLICT (user_id) DO NOTHING
        """
            )
        )
        print("✓ Migrated premium users to grandfathered Pro")

        # 5. Update feature_limits constraints
        if await table_exists(conn, "feature_limits"):
            # Drop old constraint
            await conn.execute(
                text(
                    """
                ALTER TABLE feature_limits
                DROP CONSTRAINT IF EXISTS valid_role
            """
                )
            )

            # Add new constraint with 'business' role
            await conn.execute(
                text(
                    """
                ALTER TABLE feature_limits
                ADD CONSTRAINT valid_role
                CHECK (role IN ('user', 'premium', 'business', 'admin', 'owner'))
            """
                )
            )
            print("✓ Updated feature_limits constraints")

            # Insert business role limits
            await conn.execute(
                text(
                    """
                INSERT INTO feature_limits (role, ai_limit, storage_limit_bytes, description)
                VALUES (
                    'business',
                    50.00,
                    53687091200,
                    'Business tier: $50 AI limit, 50GB storage'
                )
                ON CONFLICT (role) DO NOTHING
            """
                )
            )
            print("✓ Added business tier limits")

            # Update premium role limits (Pro tier)
            await conn.execute(
                text(
                    """
                UPDATE feature_limits
                SET
                    ai_limit = 10.00,
                    storage_limit_bytes = 5368709120,
                    description = 'Pro tier: $10 AI limit, 5GB storage'
                WHERE role = 'premium'
            """
                )
            )
            print("✓ Updated premium (Pro) tier limits")

        # 6. Add openrouter_api_token field to users
        if not await column_exists(conn, "users", "openrouter_api_token"):
            await conn.execute(
                text(
                    """
                ALTER TABLE users
                ADD COLUMN openrouter_api_token VARCHAR(255)
            """
                )
            )
            print("✓ Added openrouter_api_token field to users")

    print("✅ Billing migration completed successfully")


async def downgrade() -> None:
    """Remove billing tables."""
    print("Removing billing support...")

    async with engine.begin() as conn:
        # Drop tables in reverse order
        if await table_exists(conn, "subscription_history"):
            await conn.execute(
                text("DROP TABLE IF EXISTS subscription_history CASCADE")
            )
            print("✓ Dropped subscription_history table")

        if await table_exists(conn, "stripe_webhook_events"):
            await conn.execute(
                text("DROP TABLE IF EXISTS stripe_webhook_events CASCADE")
            )
            print("✓ Dropped stripe_webhook_events table")

        if await table_exists(conn, "subscriptions"):
            await conn.execute(text("DROP TABLE IF EXISTS subscriptions CASCADE"))
            print("✓ Dropped subscriptions table")

        # Revert feature_limits constraint
        if await table_exists(conn, "feature_limits"):
            await conn.execute(
                text(
                    """
                ALTER TABLE feature_limits
                DROP CONSTRAINT IF EXISTS valid_role
            """
                )
            )
            await conn.execute(
                text(
                    """
                ALTER TABLE feature_limits
                ADD CONSTRAINT valid_role
                CHECK (role IN ('user', 'premium', 'admin', 'owner'))
            """
                )
            )
            await conn.execute(
                text("DELETE FROM feature_limits WHERE role = 'business'")
            )
            print("✓ Reverted feature_limits constraints")

        # Remove openrouter_api_token field
        if await column_exists(conn, "users", "openrouter_api_token"):
            await conn.execute(
                text("ALTER TABLE users DROP COLUMN openrouter_api_token")
            )
            print("✓ Removed openrouter_api_token field")

    print("✅ Billing rollback completed successfully")


async def main() -> None:
    """Run migration."""
    import argparse

    parser = argparse.ArgumentParser(description="Billing tables migration")
    parser.add_argument("action", choices=["upgrade", "downgrade"])
    args = parser.parse_args()

    if args.action == "upgrade":
        await upgrade()
    elif args.action == "downgrade":
        await downgrade()

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
