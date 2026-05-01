"""
SVU BOT - NLP PIPELINE STEP 4: OUTPUT ADAPTER
=============================================
Purpose:
    This module is a post-generation processor. It takes the raw output from
    the AI and "adapts" it to match the university's communication standards.

Responsibilities (Member 4):
    1. Strip leaked framework logs, system prompt text, and telemetry lines.
    2. Enrich text with useful administrative links based on the response content.
    3. Normalize tone or formatting if the AI becomes too informal.
    4. Inject mandatory footers or contact details for specific response types.

Returns:
    An enriched and formatted string ready for the end-user.
"""

import re

# Patterns that indicate leaked internal data – never shown to the user
_LEAK_PATTERNS = [
    # Phoenix framework log lines  (e.g. "2026-05-01T11:30:46 - Phoenix AI.Insight - INFO - ...")
    r'^\d{4}-\d{2}-\d{2}T[\d:.]+\s*-\s*Phoenix AI\..*$',
    # Lines that start with the raw system prompt keyword
    r'^System:\s+You are.*$',
    # "Question:" label injected by RAG pipeline
    r'^Question:\s+.*$',
    # "Context:" label injected by RAG pipeline
    r'^Context[:\s].*$',
    # Telemetry / latency dump lines
    r'.*Latency:.*Tokens:.*$',
    r'.*Request Completed:.*$',
    r'.*HyDE Answer Generated:.*$',
    r'.*Retrieving Knowledge.*$',
    r'.*Retrieved \d+ unique documents.*$',
    r'.*Progress: \d+/\d+ units indexed.*$',
    r'.*indexed\.\.\.$',
]

_LEAK_RE = re.compile('|'.join(_LEAK_PATTERNS), re.MULTILINE | re.IGNORECASE)


class OutputAdapter:
    """Handled by Member 4 of the NLP team."""

    @staticmethod
    def sanitize(raw: str) -> str:
        """Remove any framework/log/system-prompt lines from the LLM output."""
        if not raw:
            return raw

        # Remove entire lines that match leak patterns
        lines = raw.splitlines()
        clean_lines = [ln for ln in lines if not _LEAK_RE.match(ln.strip())]
        result = '\n'.join(clean_lines).strip()

        # Edge-case: entire response was noise → return a safe fallback
        if not result:
            return "I'm sorry, I couldn't process that request. Please try again."

        return result

    @staticmethod
    def process(llm_output: str) -> str:
        # 1. Remove any leaked internal data first
        clean = OutputAdapter.sanitize(llm_output)

        # 2. If the bot mentions a program, ensure the official link is present
        if "program" in clean.lower():
            if "https://www.svuonline.org/en/programs" not in clean:
                clean += "\n\n🔗 [Official Programs Page](https://www.svuonline.org/en/programs)"

        return clean
