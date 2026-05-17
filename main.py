"""Ebook-Normalizer — pipeline entry point.

Scans a folder of EPUB files, enriches metadata via an AI provider, and
renames each file to a consistent, library-sortable format.

Usage
-----
    python main.py [--dry-run] [--live] [--max-files N] [--reset-state]

See README.md for full configuration details.
"""

import argparse
import os
from typing import Any, Dict

from ai_providers.registry import get_provider
from audit_logger import init_audit_log, write_audit_row
from config import AI_PROVIDER, BOOKS_FOLDER, DRY_RUN, MAX_FILES
from epub_reader import extract_epub_metadata, extract_text_sample
from renamer import FILENAME_PATTERN, build_filename, rename_file
from state_manager import load_state, mark_processed, save_state

ai = get_provider(AI_PROVIDER)


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------


def process_folder(folder: str, dry_run: bool, max_files: int) -> None:
    """Walk *folder* and normalize every unprocessed EPUB file.

    Args:
        folder:    Root directory to scan (recursive).
        dry_run:   When ``True``, log proposed renames without touching files.
        max_files: Stop after this many files are processed in this run.
    """
    state = load_state()
    processed_paths: set[str] = set(state.get("processed", []))

    init_audit_log()

    count = 0

    try:
        for root, _, files in os.walk(folder):
            for filename in files:
                full_path = os.path.join(root, filename)

                # Guard: skip non-files (symlinks to dirs, etc.)
                if not os.path.isfile(full_path):
                    print(f"Skipping (not a file) → {filename}")
                    continue

                # Only process EPUBs
                if not filename.lower().endswith(".epub"):
                    print(f"Skipping (not EPUB) → {filename}")
                    continue

                # Skip files already handled in a previous run
                if full_path in processed_paths:
                    print(f"Already processed → {filename}")
                    continue

                # Skip files already in normalized format
                if FILENAME_PATTERN.match(filename):
                    print(f"Already normalized → {filename}")
                    write_audit_row(
                        {
                            "original_filename": filename,
                            "new_filename": filename,
                            "title": "",
                            "author_first": "",
                            "author_last": "",
                            "series": "",
                            "series_number": "",
                            "ai_used": "no",
                            "renamed": "no",
                            "skipped_reason": "already_normalized",
                        }
                    )
                    mark_processed(state, full_path)
                    continue

                print(f"\nProcessing: {filename}")

                # --- Extract ---------------------------------------------------
                try:
                    metadata = extract_epub_metadata(full_path)
                    text_sample = extract_text_sample(full_path)
                except Exception as e:
                    print(f"Error reading EPUB: {e}")
                    write_audit_row(
                        {
                            "original_filename": filename,
                            "new_filename": filename,
                            "title": "",
                            "author_first": "",
                            "author_last": "",
                            "series": "",
                            "series_number": "",
                            "ai_used": "no",
                            "renamed": "no",
                            "skipped_reason": "epub_read_error",
                        }
                    )
                    mark_processed(state, full_path)
                    continue

                # --- Enrich ----------------------------------------------------
                ai_meta = ai.identify_book(filename, metadata, text_sample)

                final_meta: Dict[str, Any] = {
                    "title": ai_meta.get("title") or metadata.get("title"),
                    "author_first": ai_meta.get("author_first"),
                    "author_last": ai_meta.get("author_last"),
                    "series": ai_meta.get("series"),
                    "series_number": ai_meta.get("series_number"),
                }

                new_name = build_filename(final_meta)

                # --- Dry run ---------------------------------------------------
                if dry_run:
                    print(f"[DRY RUN] → {new_name}")
                    write_audit_row(
                        {
                            "original_filename": filename,
                            "new_filename": new_name,
                            "title": final_meta.get("title", ""),
                            "author_first": final_meta.get("author_first", ""),
                            "author_last": final_meta.get("author_last", ""),
                            "series": final_meta.get("series", ""),
                            "series_number": final_meta.get("series_number", ""),
                            "ai_used": "yes",
                            "renamed": "no",
                            "skipped_reason": "dry_run",
                        }
                    )
                    mark_processed(state, full_path)
                    continue

                # --- Rename ----------------------------------------------------
                new_path = rename_file(full_path, new_name)
                renamed = new_path is not None

                write_audit_row(
                    {
                        "original_filename": filename,
                        "new_filename": new_name,
                        "title": final_meta.get("title", ""),
                        "author_first": final_meta.get("author_first", ""),
                        "author_last": final_meta.get("author_last", ""),
                        "series": final_meta.get("series", ""),
                        "series_number": final_meta.get("series_number", ""),
                        "ai_used": "yes",
                        "renamed": "yes" if renamed else "no",
                        "skipped_reason": "" if renamed else "name_conflict",
                    }
                )

                mark_processed(state, full_path)

                count += 1
                if count >= max_files:
                    print(f"\nReached MAX_FILES = {max_files}. Stopping.")
                    return

    finally:
        # Always persist state — even on crash or KeyboardInterrupt.
        save_state(state)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ebook-normalizer",
        description="Normalize EPUB filenames using AI-assisted metadata enrichment.",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--dry-run",
        action="store_true",
        default=None,
        help="Preview renames without touching files (overrides DRY_RUN env var).",
    )
    mode.add_argument(
        "--live",
        action="store_true",
        help="Apply renames for real (overrides DRY_RUN=true in .env).",
    )
    parser.add_argument(
        "--max-files",
        type=int,
        default=MAX_FILES,
        metavar="N",
        help=f"Stop after N files this run (default: {MAX_FILES}).",
    )
    parser.add_argument(
        "--reset-state",
        action="store_true",
        help="Clear the processed-files state before running (re-process everything).",
    )
    return parser


if __name__ == "__main__":
    if not BOOKS_FOLDER:
        raise ValueError("BOOKS_FOLDER is not set in the .env file.")

    args = _build_parser().parse_args()

    # Resolve dry-run: CLI flags take priority over .env
    if args.live:
        effective_dry_run = False
    elif args.dry_run:
        effective_dry_run = True
    else:
        effective_dry_run = DRY_RUN

    if args.reset_state:
        save_state({"processed": []})
        print("State cleared.")

    mode_label = "DRY RUN" if effective_dry_run else "LIVE"
    print(f"Starting Ebook-Normalizer [{mode_label}] — max files: {args.max_files}")

    process_folder(BOOKS_FOLDER, dry_run=effective_dry_run, max_files=args.max_files)
