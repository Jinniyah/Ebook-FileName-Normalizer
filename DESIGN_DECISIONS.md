# Design Decisions — Ebook-Normalizer

> This document records the key architectural choices made during development,
> the reasoning behind each, and the trade-offs considered.  It is intended
> for future maintainers, portfolio reviewers, and for the author's own
> reference when revisiting the project.



---

## 1. Local-First Architecture

**Decision:** The tool runs entirely on the local machine.  EPUB files are
never uploaded to a remote service.  Only truncated text samples are sent
outbound (to the LLM API).

**Rationale:**
- Personal ebook libraries contain books the user paid for or legally
  acquired.  Uploading them to a cloud service raises copyright and privacy
  concerns that a local tool sidesteps entirely.
- Local execution removes the need for authentication, storage costs, egress
  fees, and service reliability dependencies.
- The tool's job is a one-time normalization task — cloud infrastructure
  would be engineering overhead with no benefit.

**Trade-off:** Users must run the tool themselves and manage their own API
key.  This is appropriate for a personal utility.

---

## 2. Pluggable AI Provider Pattern (Strategy Pattern)

**Decision:** All LLM interaction is behind an abstract `AIProvider` base
class.  `OpenAIProvider` and `NullProvider` are two concrete implementations.
New providers are registered in a central registry (`ai_providers/registry.py`)
without touching the pipeline.

**Rationale:**
- The LLM market is moving fast.  OpenAI may not be the best or cheapest
  option in a year.  Anthropic Claude, local models (Ollama, LM Studio), and
  Gemini are all plausible replacements.
- The pipeline logic (walk folder → extract → enrich → rename → log) does not
  care which model performs the enrichment.  Coupling the two would make
  swapping providers unnecessarily painful.
- The `NullProvider` enables fully offline operation and deterministic testing
  without any mocking of external APIs.

**Trade-off:** A small amount of indirection.  For a single-provider tool this
might feel like over-engineering, but the pattern pays for itself the first
time a provider is swapped.

---

## 3. JSON State File for Idempotency

**Decision:** A `state.json` file tracks which file paths have already been
processed.  Re-running the tool skips any path in that list.

**Rationale:**
- EPUB libraries can be large.  API calls cost money.  Running the tool twice
  over a 500-book library without state would double the cost.
- A JSON file is human-readable, trivially inspectable, and easy to reset
  (`--reset-state` flag or delete the file).
- SQLite was considered but adds a dependency and schema management for what
  is essentially a set of strings.

**Trade-off:** The state file tracks paths, not content hashes.  If a file is
moved to a different folder, it will be re-processed.  For a personal library
tool this is acceptable — re-processing a file that has already been renamed
is harmless because the normalised filename will match `FILENAME_PATTERN` and
be skipped again.

**Flush on every mark:** State is written to disk after every file is marked
processed (not only at the end of a run).  This ensures progress survives a
crash, keyboard interrupt, or API rate-limit failure mid-batch.

---

## 4. CSV Audit Log

**Decision:** Every file action — rename, dry-run preview, skip, error — is
appended to `audit_log.csv`.

**Rationale:**
- Renaming files is a destructive, irreversible operation.  Having a complete
  record of what was done (and what was proposed) makes it possible to audit
  the run and plan a rollback if needed.
- CSV opens in Excel/LibreOffice with no tooling.  It can be filtered, sorted,
  and shared without any special software.
- Append-only logging is safe to interrupt — partial runs produce a valid log.

**Schema choices:**
- `timestamp` (UTC ISO 8601) — added so multiple runs can be distinguished in
  the same log file.
- `ai_used` — distinguishes metadata-only rows (NullProvider / already-
  normalised) from AI-enriched rows.
- `skipped_reason` — enumerated values (`dry_run`, `already_normalized`,
  `epub_read_error`, `name_conflict`) make the log filterable by outcome.

**Trade-off:** The log grows unbounded.  For a personal library this is fine;
a production system would rotate logs.

---

## 5. Dry-Run Default

**Decision:** `DRY_RUN=true` is the default in `.env.example` and the
`--dry-run` flag is the safer CLI default.

**Rationale:**
- Renaming files is not easily undone.  A user running the tool for the first
  time should always be able to review proposed changes before committing them.
- The `audit_log.csv` produced by a dry run serves as a preview manifest.
- This follows the principle of least surprise for a tool that modifies the
  filesystem.

**Trade-off:** Users must consciously opt in to real renames with `--live`
or `DRY_RUN=false`.  This is the intended behaviour.

---

## 6. Filename Format

**Decision:** The normalised format is:

```
Lastname, Firstname — Series #01 — Title.epub
Lastname, Firstname — Title.epub
```

**Rationale:**
- **Last name first** sorts correctly in any file browser or e-reader by
  author family name, which is the natural sort order for a library.
- **Em dash (—) as separator** is visually distinct, unlikely to appear in
  real titles, and not an illegal filesystem character on any platform.
- **Zero-padded series number (`#01`)** ensures alphabetical sort matches
  reading order for series up to 99 books.  `#ZZ` is used when the series
  is known but the number is not, so those files sort to the end of the
  series rather than to a random position.
- The format is **parseable** — `FILENAME_PATTERN` can reliably detect
  already-normalised files without false positives.

**Trade-off:** Em dashes can be awkward to type if a user wants to manually
create a file in this format.  This was accepted as a reasonable trade-off
for visual clarity.

---

## 7. AI Prompt Design

**Decision:** The OpenAI prompt instructs the model to act as a
"bibliographic metadata engine" and return *only* a JSON object with five
specific fields.  It includes concrete examples of correct normalization and
explicit rules for stripping series information from the title.

**Rationale:**
- Structured output (JSON) is essential because the result feeds directly into
  filename construction.  Free-form prose would require fragile parsing.
- `temperature=0` is used to maximise determinism — the same input should
  produce the same output across runs.
- `gpt-4o-mini` was chosen for cost efficiency.  The task (bibliographic
  identification) is well within the capability of a smaller model, and the
  structured prompt constrains the output space significantly.
- The prompt explicitly permits the model to use general world knowledge about
  published books and series, which is the primary value it adds over simple
  regex.

**Fallback:** If the model returns malformed JSON, `_safe_parse_json` attempts
to extract a JSON object from the response using a regex before giving up and
returning an empty dict.  This handles cases where the model wraps its
response in markdown fences.

---

## 8. No Shell Execution / No Dynamic Code Loading

**Decision:** The tool uses no `subprocess`, `eval`, `exec`, or dynamic
imports at runtime.

**Rationale:**
- The tool processes files from arbitrary folders, including potentially
  untrusted sources (downloaded EPUBs).  Avoiding shell execution prevents
  any possibility of a crafted filename triggering a command injection.
- This is documented in `THREAT_MODEL.md` under Elevation of Privilege.

---

## 9. MAX_FILES Safety Cap

**Decision:** Processing stops after `MAX_FILES` files per run (default: 50).

**Rationale:**
- A first run on a large library without a cap could generate hundreds of API
  calls before the user has had a chance to review a dry-run output.
- The cap provides a natural "batch size" — run, review, run again — which is
  a safer workflow for an irreversible operation.
- The state file ensures the next run picks up where the previous one stopped.

---

## 10. What I Would Do Differently at Scale

If this tool were extended to manage a shared library or run as a service:

- **Replace the JSON state file with SQLite.**  A database handles concurrent
  access, supports queries ("which files had name conflicts?"), and scales to
  millions of records.
- **Add a content hash to the state.**  Track files by SHA-256 of their
  content, not just path, so renames and moves don't trigger reprocessing.
- **Structured logging** (e.g., `structlog`) instead of `print()` statements,
  with log levels and machine-readable output.
- **Async API calls** to process multiple files concurrently and respect rate
  limits with a token-bucket implementation.
- **A thin CLI front-end** (e.g., `typer` or `click`) for richer argument
  handling, `--help` output, and shell completion.
- **Provider-level retry / backoff** so transient API errors don't abort an
  entire run.
