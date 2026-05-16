import os
from typing import Dict, Any

from config import AI_PROVIDER, DRY_RUN, MAX_FILES
from epub_reader import extract_epub_metadata, extract_text_sample
from renamer import build_filename, rename_file, FILENAME_PATTERN
from state_manager import load_state, save_state, mark_processed
from audit_logger import init_audit_log, write_audit_row

from config import AI_PROVIDER, OPENAI_API_KEY
from config import BOOKS_FOLDER


if AI_PROVIDER == "openai":
    if OPENAI_API_KEY:
        from ai_providers.openai_provider import OpenAIProvider as ProviderClass
    else:
        from ai_providers.null_provider import NullProvider as ProviderClass
else:
    raise ValueError(f"Unsupported AI provider: {AI_PROVIDER}")

ai = ProviderClass()


def process_folder(folder: str) -> None:
    state = load_state()
    processed_paths = set(state.get("processed", []))

    init_audit_log()

    count = 0

    for root, _, files in os.walk(folder):
        for filename in files:            
            full_path = os.path.join(root, filename)
            
            # Skip directories or weird filesystem entries
            if not os.path.isfile(full_path):
                print(f"Skipping (not a file) → {filename}")
                continue

            # Skip anything that is not an EPUB
            if not filename.lower().endswith(".epub"):
                print(f"Skipping (not EPUB) → {filename}")
                continue                       

            # Already processed?
            if full_path in processed_paths:
                print(f"Already processed → {filename}")
                continue

            # Already normalized?
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

            # AI enrichment
            ai_meta = ai.identify_book(filename, metadata, text_sample)

            final_meta: Dict[str, Any] = {
                "title": ai_meta.get("title") or metadata.get("title"),
                "author_first": ai_meta.get("author_first"),
                "author_last": ai_meta.get("author_last"),
                "series": ai_meta.get("series"),
                "series_number": ai_meta.get("series_number"),
            }

            new_name = build_filename(final_meta)

            if DRY_RUN:
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

            # Real rename
            new_path = rename_file(full_path, new_name)

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
                    "renamed": "yes" if new_path else "no",
                    "skipped_reason": "" if new_path else "name_conflict",
                }
            )

            mark_processed(state, full_path)

            count += 1
            if count >= MAX_FILES:
                print(f"\nReached MAX_FILES = {MAX_FILES}. Stopping.")
                save_state(state)
                return

    save_state(state)


if __name__ == "__main__":
    if not BOOKS_FOLDER:
        raise ValueError("BOOKS_FOLDER is not set in the .env file")

    process_folder(BOOKS_FOLDER)