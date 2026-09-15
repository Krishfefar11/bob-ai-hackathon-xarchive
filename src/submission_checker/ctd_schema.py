"""ICH M4 Common Technical Document (CTD) module/section structure.

Modules 2-5 follow the harmonized ICH M4 numbering. Module 1 is region-specific (not
part of the harmonized CTD) — the entries below are illustrative US FDA-style headings.
"""

CTD_SCHEMA = {
    "Module 1": {
        "title": "Administrative Information (region-specific, not harmonized)",
        "sections": {
            "1.1": "Table of Contents (Module 1)",
            "1.2": "Application Forms / Cover Letter",
            "1.3": "Product Information / Labeling",
            "1.4": "Administrative Information (e.g. patent, exclusivity)",
        },
    },
    "Module 2": {
        "title": "CTD Summaries",
        "sections": {
            "2.1": "CTD Table of Contents",
            "2.2": "CTD Introduction",
            "2.3": "Quality Overall Summary",
            "2.4": "Nonclinical Overview",
            "2.5": "Clinical Overview",
            "2.6": "Nonclinical Written and Tabulated Summaries",
            "2.7": "Clinical Summary",
        },
    },
    "Module 3": {
        "title": "Quality",
        "sections": {
            "3.1": "Table of Contents of Module 3",
            "3.2": "Body of Data",
            "3.3": "Literature References",
        },
    },
    "Module 4": {
        "title": "Nonclinical Study Reports",
        "sections": {
            "4.1": "Table of Contents of Module 4",
            "4.2": "Study Reports",
            "4.3": "Literature References",
        },
    },
    "Module 5": {
        "title": "Clinical Study Reports",
        "sections": {
            "5.1": "Table of Contents of Module 5",
            "5.2": "Tabular Listing of All Clinical Studies",
            "5.3": "Clinical Study Reports",
            "5.4": "Literature References",
        },
    },
}
