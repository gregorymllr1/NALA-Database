"""
One-command weekly maintainer workflow.

Runs, in order:
1. git pull --rebase
2. Extraction.py
3. ingestion.py
4. Upload nala_rd_data.db to Cloudflare R2 (data.naladatabase.us)

Use --dry-run first to preview actions safely.

Requires R2 credentials in environment variables (or a .env file in the project root):
  R2_ACCOUNT_ID         — your Cloudflare account ID
  R2_ACCESS_KEY_ID      — R2 API token Access Key ID
  R2_SECRET_ACCESS_KEY  — R2 API token Secret Access Key
  R2_BUCKET             — bucket name (defaults to 'nala-data')
  R2_OBJECT_KEY         — object key in the bucket (defaults to 'nala_rd_data.db')
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
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


def upload_to_r2(dry_run: bool = False) -> None:
    # Lazy imports so users without boto3 installed get a clear error only when uploading
    try:
        import boto3  # type: ignore[import-not-found]
        from botocore.config import Config  # type: ignore[import-not-found]
    except ImportError as exc:
        raise RuntimeError(
            "boto3 is required for R2 upload. Install it: pip install boto3 python-dotenv"
        ) from exc

    # Load .env if python-dotenv is available; otherwise rely on the environment
    try:
        from dotenv import load_dotenv  # type: ignore[import-not-found]
        load_dotenv(PROJECT_ROOT / ".env")
    except ImportError:
        pass

    account_id = os.environ.get("R2_ACCOUNT_ID")
    access_key = os.environ.get("R2_ACCESS_KEY_ID")
    secret_key = os.environ.get("R2_SECRET_ACCESS_KEY")
    bucket     = os.environ.get("R2_BUCKET", "nala-data")
    object_key = os.environ.get("R2_OBJECT_KEY", "nala_rd_data.db")

    missing = [name for name, val in {
        "R2_ACCOUNT_ID": account_id,
        "R2_ACCESS_KEY_ID": access_key,
        "R2_SECRET_ACCESS_KEY": secret_key,
    }.items() if not val]
    if missing:
        raise RuntimeError(
            "Missing required R2 environment variables: " + ", ".join(missing) +
            ". Set them in your shell or in a .env file in the project root."
        )

    endpoint = f"https://{account_id}.r2.cloudflarestorage.com"
    size_mb = DB_FILE.stat().st_size / (1024 * 1024)
    _print_step(f"Uploading {DB_FILE.name} ({size_mb:.1f} MB) to R2 bucket '{bucket}' as '{object_key}'")

    if dry_run:
        _print_step("Dry-run: skipping actual upload.")
        return

    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name="auto",
        config=Config(signature_version="s3v4"),
    )
    client.upload_file(
        Filename=str(DB_FILE),
        Bucket=bucket,
        Key=object_key,
        ExtraArgs={"ContentType": "application/octet-stream"},
    )
    _print_step("R2 upload complete.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run weekly database update workflow.")
    parser.add_argument(
        "--message",
        default=f"Weekly database update: {dt.date.today().isoformat()}",
        help="(Reserved for future use.) Note describing this run.",
    )
    parser.add_argument(
        "--skip-pull",
        action="store_true",
        help="Skip git pull --rebase before extraction.",
    )
    parser.add_argument(
        "--skip-upload",
        action="store_true",
        help="Run extraction/ingestion but skip the R2 upload step.",
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
            _print_step("Dry-run complete. No files were modified or uploaded.")
            return 0

        if args.skip_upload:
            _print_step("R2 upload skipped by --skip-upload.")
            return 0

        upload_to_r2(dry_run=args.dry_run)
        _print_step("Workflow complete: database extracted, ingested, and uploaded to R2.")
        return 0

    except Exception as exc:
        _print_step(f"ERROR: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
