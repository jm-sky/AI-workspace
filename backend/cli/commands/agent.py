"""Agent / chat maintenance CLI commands."""

import asyncio
from datetime import UTC, datetime

import typer
from rich.console import Console

from ..main import COMMAND_GROUPS, show_group_interactive_menu

agent_app = typer.Typer(
    name="agent",
    help="Agent and chat maintenance commands",
    no_args_is_help=False,
)

console = Console()


@agent_app.callback(invoke_without_command=True)
def agent_callback(ctx: typer.Context) -> None:
    """Show interactive menu when no subcommand is provided."""
    if ctx.invoked_subcommand is None:
        show_group_interactive_menu("agent", COMMAND_GROUPS["agent"])


@agent_app.command("purge-orphans")
def purge_orphans(
    hours: int | None = typer.Option(
        None,
        "--hours",
        help="Override ATTACHMENT_ORPHAN_TTL_HOURS (default from settings)",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="List how many orphans would be deleted without deleting",
    ),
) -> None:
    """Delete chat attachments never bound to a run (run_id IS NULL).

    Examples:
        python -m cli agent purge-orphans
        python -m cli agent purge-orphans --hours 24
        python -m cli agent purge-orphans --dry-run
    """
    asyncio.run(_purge_orphans_async(hours=hours, dry_run=dry_run))


async def _purge_orphans_async(*, hours: int | None, dry_run: bool) -> None:
    from app.core.config import settings
    from app.core.database import get_db
    from app.modules.agent.services.chat_attachment_service import ChatAttachmentService

    ttl = hours if hours is not None else settings.attachments.orphan_ttl_hours
    async for db in get_db():
        service = ChatAttachmentService(db)
        count = await service.purge_orphans(older_than_hours=ttl, dry_run=dry_run)
        mode = "would delete" if dry_run else "deleted"
        console.print(
            f"[green]Orphan purge[/green] {mode} [cyan]{count}[/cyan] "
            f"attachment(s) older than {ttl}h "
            f"(as of {datetime.now(UTC).isoformat()})"
        )
        return
