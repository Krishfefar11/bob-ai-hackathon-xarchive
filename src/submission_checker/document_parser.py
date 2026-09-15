"""Extracts text and detects CTD-style section numbers from an uploaded regulatory document."""
import io
import re

import PyPDF2
from docx import Document

# Anchored to the start of a line (optionally after a bullet/dash) and required to be
# followed by more text on that line — matches a real heading like "2.3 Quality Overall
# Summary" but not a bare in-sentence mention like "as described in section 2.3, ...".
# Without this anchor, a guideline document that merely *explains* the CTD format (and so
# mentions nearly every section number while describing it) reads as a 100%-complete dossier.
# The optional trailing "\.?" handles official EU/ICH numbering like "2.3. Quality Overall
# Summary" — a period right after the number, before the title — which is otherwise common
# enough (it's ICH's own convention) that skipping it misses real headings entirely.
_SECTION_PATTERN = re.compile(r"^[ \t]*[•\-*]?[ \t]*([1-5](?:\.\d+){1,3})\.?(?=[ \t]+\S)", re.MULTILINE)


def extract_text(file_obj, filename: str) -> str:
    suffix = filename.lower().rsplit(".", 1)[-1]

    if suffix == "pdf":
        reader = PyPDF2.PdfReader(file_obj)
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    if suffix == "docx":
        document = Document(io.BytesIO(file_obj.read()))
        return "\n".join(p.text for p in document.paragraphs)

    if suffix == "txt":
        raw = file_obj.read()
        return raw.decode("utf-8", errors="ignore") if isinstance(raw, bytes) else raw

    raise ValueError(f"Unsupported file type: .{suffix} (expected .pdf, .docx, or .txt)")


def detect_section_numbers(text: str) -> set:
    # PDF text extraction doesn't reliably preserve real line breaks — headings that are
    # visually on their own line can come back joined by a wide run of spaces instead of a
    # newline. Treat 3+ consecutive spaces/tabs as an implicit line break too, so a heading
    # isn't missed just because PyPDF2 didn't emit a literal \n before it.
    normalized = re.sub(r"[ \t]{3,}", "\n", text)
    return set(_SECTION_PATTERN.findall(normalized))
