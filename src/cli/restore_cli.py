#!/usr/bin/env python3
import click
import asyncio
import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from ..database.restore_manager import RestoreManager
from ..monitoring.restore_metrics import RestoreMetricsManager
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

console = Console()
logger = logging.getLogger(__name__)

def setup_logging(verbose: bool):
    """Configure logging level"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

@click.group()
@click.option('--verbose', is_flag=True, help='Enable verbose logging')
def cli(verbose: bool):
    """SecureAI Platform Database Restore CLI"""
    setup_logging(verbose)

@cli.command()
@click.option('--limit', default=10, help='Number of backups to list')
@click.option('--format', type=click.Choice(['table', 'json']), default='table')
async def list_backups(limit: int, format: str):
    """List available database backups"""
    try:
        manager = RestoreManager()
        backups = await manager.list_available_backups()
        backups = backups[:limit]

        if format == 'json':
            console.print_json(data=backups)
            return

        table = Table(title="Available Backups")
        table.add_column("Name")
        table.add_column("Size (MB)")
        table.add_column("Created")
        table.add_column("Status")

        for backup in backups:
            size_mb = round(backup['size'] / (1024 * 1024), 2)
            created = backup['created'].strftime("%Y-%m-%d %H:%M:%S")
            status = "✅" if backup.get('checksum') else "⚠️"
            table.add_row(backup['name'], str(size_mb), created, status)

        console.print(table)

    except Exception as e:
        logger.error(f"Failed to list backups: {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('backup_name')
@click.argument('target_db')
@click.option('--verify/--no-verify', default=True, help='Verify restore after completion')
@click.option('--force', is_flag=True, help='Force restore even if target exists')
async def restore(backup_name: str, target_db: str, verify: bool, force: bool):
    """Restore a database backup"""
    try:
        manager = RestoreManager()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeElapsedColumn(),
        ) as progress:
            # Check backup exists
            task = progress.add_task("Checking backup...", total=None)
            backups = await manager.list_available_backups()
            if not any(b['name'] == backup_name for b in backups):
                progress.stop()
                console.print(f"[red]Backup {backup_name} not found[/red]")
                sys.exit(1)
            progress.update(task, completed=True)

            # Start restore
            task = progress.add_task("Restoring database...", total=None)
            success = await manager.restore_backup(backup_name, target_db)
            if not success:
                progress.stop()
                console.print("[red]Restore failed[/red]")
                sys.exit(1)
            progress.update(task, completed=True)

            # Verify if requested
            if verify:
                task = progress.add_task("Verifying restore...", total=None)
                verified = await manager._verify_restoration(target_db)
                if not verified:
                    progress.stop()
                    console.print("[red]Verification failed[/red]")
                    sys.exit(1)
                progress.update(task, completed=True)

        console.print("[green]Restore completed successfully[/green]")

    except Exception as e:
        logger.error(f"Restore failed: {str(e)}")
        sys.exit(1)

@cli.command()
async def status():
    """Show restore system status"""
    try:
        metrics = RestoreMetricsManager()
        stats = metrics.get_restore_stats()

        table = Table(title="Restore System Status")
        table.add_column("Metric")
        table.add_column("Value")

        table.add_row("In Progress", str(stats['in_progress']))
        table.add_row("Total Success", str(stats['total_success']))
        table.add_row("Total Failure", str(stats['total_failure']))
        table.add_row("Verification Success", str(stats['verification_success']))
        table.add_row("Verification Failure", str(stats['verification_failure']))

        console.print(table)

    except Exception as e:
        logger.error(f"Failed to get status: {str(e)}")
        sys.exit(1)

@cli.command()
@click.argument('backup_name')
async def verify(backup_name: str):
    """Verify a backup's integrity"""
    try:
        manager = RestoreManager()

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
        ) as progress:
            task = progress.add_task("Verifying backup...", total=None)
            verified = await manager._verify_backup(Path(backup_name), None)
            progress.update(task, completed=True)

        if verified:
            console.print("[green]Backup verification successful[/green]")
        else:
            console.print("[red]Backup verification failed[/red]")
            sys.exit(1)

    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        sys.exit(1)

def main():
    """CLI entry point"""
    try:
        asyncio.run(cli())
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(1)

if __name__ == "__main__":
    main()
