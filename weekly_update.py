"""
One-command weekly maintainer workflow.

Runs, in order:
1. git pull --rebase
2. Extraction.py
3. ingestion.py
4. git add nala_rd_data.db
5. git commit -m "..."
6. git push

Use --dry-run first to preview actions safely.
"""

from __future__ import annotations

import argparse
import datetime as dt
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent
DB_FILE = PROJECT_ROOT / "nala_rd_data.db"


def _print_step(message: str) -> None:
    print(f"\n[weekly-update] {message}")


def run_command(command: list[str], dry_run: bool = False, check: bool = True) -> int:
    rendered = " ".join(command)
    _print_step(f"$ {rendered}")

    if dry_run:
        return 0

    result = subprocess.run(command, cwd=str(PROJECT_ROOT))

    if check and result.returncode != 0:
        raise RuntimeError(f"Command failed ({result.returncode}): {rendered}")

    return result.returncode


def command_output(command: list[str]) -> str:
    result = subprocess.run(
        command,
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        raise RuntimeError(stderr or f"Failed command: {' '.join(command)}")
    return result.stdout.strip()


def ensure_git_repo() -> None:
    output = command_output(["git", "rev-parse", "--is-inside-work-tree"])
    if output.lower() != "true":
        raise RuntimeError("This script must be run inside a git repository.")


def ensure_clean_worktree(allow_dirty: bool) -> None:
    if allow_dirty:
        return

    status = command_output(["git", "status", "--porcelain"])
    if status:
        raise RuntimeError(
            "Working tree is not clean. Commit/stash existing changes first, "
            "or rerun with --allow-dirty."
        )


def database_changed() -> bool:
    status = command_output(["git", "status", "--porcelain", "--", "nala_rd_data.db"])
    return bool(status)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run weekly database update workflow.")
    parser.add_argument(
        "--message",
        default=f"Weekly database update: {dt.date.today().isoformat()}",
        help="Git commit message for the database update.",
    )
    parser.add_argument(
        "--skip-pull",
        action="store_true",
        help="Skip git pull --rebase before extraction.",
    )
    parser.add_argument(
        "--skip-push",
        action="store_true",
        help="Commit locally but do not push.",
    )
    parser.add_argument(
        "--allow-dirty",
        action="store_true",
        help="Allow running even when unrelated files are already modified.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview actions without executing commands.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    try:
        _print_step(f"Project root: {PROJECT_ROOT}")
        ensure_git_repo()
        ensure_clean_worktree(allow_dirty=args.allow_dirty)

        if not args.skip_pull:
            run_command(["git", "pull", "--rebase"], dry_run=args.dry_run)

        run_command([sys.executable, "Extraction.py"], dry_run=args.dry_run)
        run_command([sys.executable, "ingestion.py"], dry_run=args.dry_run)

        if not DB_FILE.exists() and not args.dry_run:
            raise RuntimeError("Database file missing after ingestion: nala_rd_data.db")

        if args.dry_run:
            _print_step("Dry-run complete. No files were modified.")
            return 0

        if not database_changed():
            _print_step("No changes detected in nala_rd_data.db. Nothing to commit.")
            return 0

        run_command(["git", "add", "nala_rd_data.db"])
        run_command(["git", "commit", "-m", args.message])

        if args.skip_push:
            _print_step("Commit created locally. Push skipped by --skip-push.")
        else:
            run_command(["git", "push"])
            _print_step("Workflow complete: database updated, committed, and pushed.")

        return 0

    except Exception as exc:
        _print_step(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
