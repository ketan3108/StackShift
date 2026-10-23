"""StackShift CLI entry point."""

from typing import Annotated

import typer

from stackshift import __version__

app = typer.Typer(
    help="Measure embedding-model drift and manage safe adapter cutovers.",
    invoke_without_command=True,
)


def _unavailable(command: str) -> None:
    """Explain that a command is intentionally gated, then exit predictably."""
    typer.echo(f"{command} is not available until its gated implementation phase.", err=True)
    raise typer.Exit(code=2)


@app.callback()
def main(
    version: Annotated[bool, typer.Option("--version", help="Print version and exit")] = False,
) -> None:
    """StackShift command line interface."""
    if version:
        typer.echo(__version__)
        raise typer.Exit()


for _name in ("scan", "train", "validate", "cutover", "rollback", "ingest", "report"):
    app.command(name=_name, help=f"{_name} (not implemented in Phase 0)")(
        lambda name=_name: _unavailable(name)
    )
