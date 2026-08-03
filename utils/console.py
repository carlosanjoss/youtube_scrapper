import logging
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.rule import Rule
from rich.table import Table
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
    TimeRemainingColumn,
)

from config import BASE_DIR

# ── Log file ──────────────────────────────────────────────────────

_LOG_DIR = BASE_DIR / "logs"
_LOG_DIR.mkdir(parents=True, exist_ok=True)
_log_file = _LOG_DIR / f"scraper_{datetime.now().strftime('%Y-%m-%d')}.log"

_logger = logging.getLogger("youtube_scraper")

if not _logger.handlers:
    _logger.setLevel(logging.DEBUG)
    _logger.propagate = False

    _handler = logging.FileHandler(_log_file, encoding="utf-8")
    _handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    _logger.addHandler(_handler)

# ── Terminal ──────────────────────────────────────────────────────

_out = Console(highlight=False)


# ── Public API ────────────────────────────────────────────────────

def header(title: str, subtitle: str | None = None):
    text = f"[bold cyan]{title}[/bold cyan]"
    if subtitle:
        text += f"\n[dim]{subtitle}[/dim]"

    _out.print()
    _out.print(Panel(text, border_style="cyan", padding=(1, 4), expand=False))
    _logger.info("=== %s%s ===", title, f" — {subtitle}" if subtitle else "")


def section(title: str):
    _out.print()
    _out.print(Rule(f"[bold cyan]{title}[/bold cyan]", style="dim cyan"))
    _logger.info("--- %s ---", title)


def info(label: str, value):
    _out.print(f"  [dim]{label}[/dim]: [white]{value}[/white]")
    _logger.info("%s: %s", label, value)


def ok(text: str):
    _out.print(f"  [green]✓[/green] {text}")
    _logger.info(text)


def skip(text: str):
    _out.print(f"  [yellow]↷[/yellow] {text}")
    _logger.info("[SKIP] %s", text)


def warn(text: str):
    _out.print(f"  [yellow]⚠[/yellow]  {text}")
    _logger.warning(text)


def fail(text: str):
    _out.print(f"  [red]✗[/red] {text}")
    _logger.error(text)


def debug(text: str):
    """Registra apenas no arquivo de log, não no terminal."""
    _logger.debug(text)


def make_progress() -> Progress:
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}"),
        BarColumn(bar_width=30),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        TimeRemainingColumn(),
        TextColumn("[green]✓ {task.fields[ok]}"),
        TextColumn("[yellow]↷ {task.fields[skipped]}"),
        TextColumn("[red]✗ {task.fields[failed]}"),
        TextColumn("[magenta]💬 {task.fields[comments]}"),
        console=_out,
        transient=False,
    )


def summary(stats):
    table = Table(
        title="[bold]Resumo da execução[/bold]",
        show_header=True,
        header_style="bold cyan",
        border_style="cyan",
        min_width=44,
        padding=(0, 1),
    )
    table.add_column("Métrica", style="dim")
    table.add_column("Valor", justify="right", style="bold white")

    table.add_row("Vídeos encontrados",    str(stats.total_videos))
    table.add_row("Vídeos processados",    str(stats.processed_videos))
    table.add_row("Vídeos pulados",        str(stats.skipped_videos))
    table.add_row("Vídeos com erro",       str(stats.failed_videos))
    table.add_row("Comentários coletados", str(stats.collected_comments))
    table.add_section()
    table.add_row("Run ID", f"[dim]{stats.run_id}[/dim]")

    _out.print()
    _out.print(table)

    _logger.info(
        "Resumo — processados: %d | pulados: %d | erros: %d | comentários: %d | run: %s",
        stats.processed_videos,
        stats.skipped_videos,
        stats.failed_videos,
        stats.collected_comments,
        stats.run_id,
    )


# ── Aliases ───────────────────────────────────────────────────────
success = ok
warning = warn
error = fail
