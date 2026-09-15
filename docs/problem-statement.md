# Problem Statement

## Who is affected

Two distinct teams inside any pharma/biotech organization, both drowning in volume:

1. **Pharmacovigilance teams** monitor drug safety after a product reaches the market. Their primary data source, FDA's FAERS database, holds 20M+ adverse event reports. Finding a genuine safety signal — a drug-event pair reported far more often than chance would predict — inside that volume by manual review takes weeks per cycle.
2. **Regulatory affairs teams** assemble Common Technical Document (CTD) dossiers to get a drug approved. A CTD submission can span 100,000+ pages across 5 modules (administrative, summaries, quality, nonclinical, clinical). Checking that every required section is present before filing is a manual, error-prone audit.

## Why existing approaches fall short

- Manual FAERS review does not scale with the data volume, and disproportionality analysis (PRR/ROR) is mechanical enough to automate but tedious enough that teams under-invest in doing it continuously.
- CTD completeness checking today is a checklist a human works through by hand against a 100+ page document — exactly the kind of structural verification a script does more reliably than a tired reviewer on their tenth review of the week.

## Why this matters *now*

- **Signal detection speed has real consequences.** Vioxx (rofecoxib) is reported to have caused 27,000+ heart attacks before its cardiovascular risk signal was acted on — a case study regulatory teams still cite for why continuous, systematic signal monitoring matters more than periodic manual review.
- **A single missing CTD section causes outright rejection.** Regulatory filings that get bounced for structural incompleteness cost 6–12 months and an estimated $50–100M in delayed time-to-market — a cost that has nothing to do with whether the drug itself is safe or effective, purely a documentation completeness failure.

## What "solved" looks like

- A pharmacovigilance reviewer can query any drug and immediately see which adverse events are statistically disproportionate for it, with the underlying counts and the standard Evans et al. (2001) criteria applied consistently.
- A regulatory affairs reviewer can upload a draft dossier and immediately see, module by module, which CTD sections are present and which are missing — before it ever reaches a human review cycle, let alone submission.

This project (P2 of the IBM Bob Hackathon) builds both as one tool. See [solution-overview.md](solution-overview.md) for how.
