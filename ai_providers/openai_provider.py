from typing import Any, Dict
import json
import re

from openai import OpenAI
from config import DEBUG_AI

from .base import AIProvider
from config import OPENAI_API_KEY, TEXT_SAMPLE_LENGTH

JSON_OBJECT_REGEX = re.compile(r"\{.*\}", re.DOTALL)


class OpenAIProvider(AIProvider):
    """OpenAI-backed implementation of AIProvider."""

    def __init__(self) -> None:
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set")
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def _safe_parse_json(self, content: str | None) -> Dict[str, Any]:
        """Extract and parse the first JSON object from the model output."""
        if not content:
            return {}

        # Try direct JSON first
        try:
            return json.loads(content)
        except Exception:
            pass

        # Try extracting the first {...} block
        match = JSON_OBJECT_REGEX.search(content)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass

        # Total failure → return empty dict
        return {}

    def identify_book(
        self, filename: str, metadata: Dict[str, Any], text_sample: str
    ) -> Dict[str, Any]:

        prompt = f"""
You are a professional bibliographic metadata engine.

Your job is to normalize book metadata into clean fields for filename generation.

You MUST return ONLY valid JSON with exactly these fields:
- "title": the book's title ONLY, with NO series name, NO series number, NO character name, NO parentheses info, NO "Book 13".
- "author_first": the primary author's first name.
- "author_last": the primary author's last name.
- "series": the series name ONLY (e.g., "Kay Scarpetta", "Jack Reacher", "Nora Kelly"), or null if not part of a series.
- "series_number": the book's number in the series as an integer, or null if not part of a series.

### RULES ###
- You MAY use your general knowledge of published books and series.
- You MAY use the filename to infer series and series_number.
- You MUST remove all series-related text from the "title" field.
- If the filename contains series info (e.g., "(Nora Kelly)", "(Jack Reacher)", "(Book 13)"), extract it into "series" and "series_number".
- If the EPUB metadata contradicts known series information, prefer your general knowledge.
- If you truly cannot determine the series, return null for both fields.
- Respond ONLY with a single JSON object. No explanation, no prose.

### Examples of correct normalization ###

Input filename: "Trace_ Scarpetta (Book 13) (Kay Scarpetta)_nodrm.epub"
Output:
{{
  "title": "Trace",
  "author_first": "Patricia",
  "author_last": "Cornwell",
  "series": "Kay Scarpetta",
  "series_number": 13
}}

Input filename: "White Fire (Pendergast Book 13)_nodrm.epub"
Output:
{{
  "title": "White Fire",
  "author_first": "Douglas",
  "author_last": "Preston",
  "series": "Pendergast",
  "series_number": 13
}}

### Provided filename ###
{filename}

### Provided EPUB metadata ###
{json.dumps(metadata, indent=2)}

### Text sample ###
{text_sample[:TEXT_SAMPLE_LENGTH]}
"""

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )

        content = response.choices[0].message.content

        parsed = self._safe_parse_json(content)

        if DEBUG_AI:
            print("PARSED JSON:")
            print(json.dumps(parsed, indent=2))
            print("="*60 + "\n")


        for key in ["title", "author_first", "author_last", "series", "series_number"]:
            parsed.setdefault(key, None)

        return parsed