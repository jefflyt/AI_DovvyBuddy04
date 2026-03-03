"""CLI utilities for content processing scripts."""

import sys
from typing import Iterator, Optional

from rich.console import Console
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)

console = Console()


def info(message: str) -> None:
    """Print info message."""
    console.print(f"[blue]ℹ[/blue] {message}")


def success(message: str) -> None:
    """Print success message."""
    console.print(f"[green]✓[/green] {message}")


def warning(message: str) -> None:
    """Print warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}", style="yellow")


def error(message: str) -> None:
    """Print error message."""
    console.print(f"[red]✗[/red] {message}", style="red")


def confirm(message: str, default: bool = False) -> bool:
    """Prompt user for yes/no confirmation.
    
    Args:
        message: Confirmation prompt
        default: Default response if user just presses Enter
        
    Returns:
        True if user confirms, False otherwise
    """
    suffix = " [Y/n]" if default else " [y/N]"
    prompt = f"{message}{suffix}: "
    
    try:
        response = input(prompt).strip().lower()
    except (KeyboardInterrupt, EOFError):
        console.print()  # New line after ^C or ^D
        return False
    
    if not response:
        return default
    
    return response in ("y", "yes")


class ProgressBar:
    """Context manager for progress bars."""
    
    def __init__(self, total: int, description: str = "Processing"):
        """Initialize progress bar.
        
        Args:
            total: Total number of items
            description: Description text
        """
        self.total = total
        self.description = description
        self.progress: Optional[Progress] = None
        self.task_id: Optional[TaskID] = None
    
    def __enter__(self) -> "ProgressBar":
        """Start progress bar."""
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed}/{task.total})"),
            TimeElapsedColumn(),
            console=console,
        )
        self.progress.__enter__()
        self.task_id = self.progress.add_task(self.description, total=self.total)
        return self
    
    def __exit__(self, *args) -> None:
        """Stop progress bar."""
        if self.progress:
            self.progress.__exit__(*args)
    
    def update(self, advance: int = 1) -> None:
        """Update progress bar.
        
        Args:
            advance: Number of items to advance
        """
        if self.progress and self.task_id is not None:
            self.progress.update(self.task_id, advance=advance)


def progress_bar(total: int, description: str = "Processing") -> ProgressBar:
    """Create a progress bar context manager.
    
    Args:
        total: Total number of items
        description: Description text
        
    Returns:
        ProgressBar context manager
        
    Example:
        with progress_bar(total=100, description="Processing files") as bar:
            for item in items:
                process(item)
                bar.update()
    """
    return ProgressBar(total, description)
