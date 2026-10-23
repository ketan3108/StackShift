"""Command-line interface."""

import json
from pathlib import Path
from typing import Annotated

import typer

from stackshift import __version__
from stackshift.artifacts.store import load_artifact
from stackshift.query.state import FileStateBackend, LiveState

app = typer.Typer(
    help="Measure embedding-model drift and manage safe adapter cutovers.",
    invoke_without_command=True,
)


def emit(payload: dict[str, object], as_json: bool) -> None:
    typer.echo(
        json.dumps(payload)
        if as_json
        else "\n".join(f"{key}: {value}" for key, value in payload.items())
    )


@app.callback()
def main(version: Annotated[bool, typer.Option("--version")] = False) -> None:
    if version:
        typer.echo(__version__)
        raise typer.Exit()


@app.command()
def scan(json_output: Annotated[bool, typer.Option("--json")] = False) -> None:
    emit(
        {
            "status": "ready",
            "metric_mode": "neighbor-overlap",
            "note": "Configure a connector and embedder through the SDK to run a corpus scan.",
        },
        json_output,
    )


@app.command()
def train(json_output: Annotated[bool, typer.Option("--json")] = False) -> None:
    emit(
        {"status": "ready", "note": "Use PairingBuilder and an adapter from the SDK."}, json_output
    )


@app.command()
def validate(json_output: Annotated[bool, typer.Option("--json")] = False) -> None:
    emit({"status": "ready", "reference": "new-model direct retrieval"}, json_output)


@app.command()
def cutover(
    state_file: Path,
    version: str,
    artifacts: Path = Path(".stackshift/artifacts"),
    yes: bool = False,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    if not yes:
        raise typer.BadParameter("pass --yes to confirm cutover")
    meta, _ = load_artifact(artifacts, version)
    FileStateBackend(str(state_file)).write(LiveState("adapter", meta.version))
    emit(
        {"status": "cutover", "adapter_version": meta.version, "propagation_bound_seconds": 15},
        json_output,
    )


@app.command()
def rollback(
    state_file: Path,
    yes: bool = False,
    json_output: Annotated[bool, typer.Option("--json")] = False,
) -> None:
    if not yes:
        raise typer.BadParameter("pass --yes to confirm rollback")
    FileStateBackend(str(state_file)).write(LiveState())
    emit({"status": "rolled-back", "propagation_bound_seconds": 15}, json_output)


@app.command()
def ingest(json_output: Annotated[bool, typer.Option("--json")] = False) -> None:
    emit(
        {"status": "ready", "note": "SDK ingestion requires an upsert-capable connector."},
        json_output,
    )


@app.command()
def report(json_output: Annotated[bool, typer.Option("--json")] = False) -> None:
    emit({"status": "ready", "text_included": False}, json_output)
