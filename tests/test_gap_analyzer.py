"""Validates CTD gap detection against a minimal synthetic document."""
import io

from submission_checker.document_parser import detect_section_numbers
from submission_checker.gap_analyzer import analyze_document


def test_detects_present_and_missing_sections():
    text = "2.3 Quality Overall Summary\n2.5 Clinical Overview\nModule 3 Quality 3.1 Table of Contents"
    found = detect_section_numbers(text)
    assert "2.3" in found
    assert "2.5" in found
    assert "2.4" not in found


_HEADINGS = (
    "2.1 CTD Table of Contents\n"
    "2.3 Quality Overall Summary\n"
    "2.5 Clinical Overview\n"
    "3.1 Table of Contents of Module 3\n"
    "3.2 Body of Data\n"
    "3.3 Literature References"
)


def test_analyze_document_txt():
    file_obj = io.BytesIO(_HEADINGS.encode("utf-8"))
    result = analyze_document(file_obj, "draft.txt")

    assert 0 < result["completeness_pct"] < 100
    assert any("2.2" in m for m in result["missing_sections"])


def test_analyze_document_ignores_inline_mentions():
    # A guideline document that merely *discusses* the CTD format (e.g. "as described in
    # section 2.3, applicants should...") must not be scored as if those sections are present.
    prose = (
        "This guideline explains how to use the CTD format.\n"
        "Module 2.1 should contain the table of contents for the dossier.\n"
        "In section 2.3, applicants provide the Quality Overall Summary.\n"
    )
    file_obj = io.BytesIO(prose.encode("utf-8"))
    result = analyze_document(file_obj, "guideline.txt")

    assert result["completeness_pct"] == 0.0


def test_detects_headings_joined_by_wide_gaps():
    # PyPDF2 doesn't always emit a real \n between visually separate lines — headings can
    # come back joined by a run of spaces instead. This mirrors that failure mode directly.
    joined = "2.1 CTD Table of Contents" + " " * 40 + "2.5 Clinical Overview" + " " * 40 + "3.1 Table of Contents"
    found = detect_section_numbers(joined)
    assert found == {"2.1", "2.5", "3.1"}


def test_per_module_completeness():
    # Module 3 fully present (3.1/3.2/3.3), Module 2 partially present (3 of 7), Module 1 empty.
    file_obj = io.BytesIO(_HEADINGS.encode("utf-8"))
    result = analyze_document(file_obj, "draft.txt")

    assert result["modules"]["Module 3"]["completeness_pct"] == 100.0
    assert result["modules"]["Module 3"]["present_count"] == 3
    assert result["modules"]["Module 2"]["present_count"] == 3
    assert result["modules"]["Module 2"]["total_count"] == 7
    assert 0 < result["modules"]["Module 2"]["completeness_pct"] < 100
    assert result["modules"]["Module 1"]["completeness_pct"] == 0.0
