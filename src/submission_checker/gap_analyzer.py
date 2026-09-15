"""Checks an extracted document's section numbers against the ICH M4 CTD structure."""
from submission_checker.ctd_schema import CTD_SCHEMA
from submission_checker.document_parser import detect_section_numbers, extract_text


def analyze_document(file_obj, filename: str) -> dict:
    text = extract_text(file_obj, filename)
    found = detect_section_numbers(text)

    modules = {}
    total_sections = 0
    present_sections = 0

    for module, info in CTD_SCHEMA.items():
        sections = {}
        module_present = 0
        for number, title in info["sections"].items():
            is_present = number in found
            sections[number] = {"title": title, "present": is_present}
            module_present += int(is_present)

        module_total = len(info["sections"])
        modules[module] = {
            "title": info["title"],
            "sections": sections,
            "completeness_pct": round(100 * module_present / module_total, 1) if module_total else 0.0,
            "present_count": module_present,
            "total_count": module_total,
        }
        total_sections += module_total
        present_sections += module_present

    completeness = round(100 * present_sections / total_sections, 1) if total_sections else 0.0
    missing = [
        f"{number} {sec['title']}"
        for module in modules.values()
        for number, sec in module["sections"].items()
        if not sec["present"]
    ]

    return {
        "modules": modules,
        "completeness_pct": completeness,
        "present_count": present_sections,
        "total_count": total_sections,
        "missing_sections": missing,
    }
