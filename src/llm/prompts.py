"""Prompt templates for watsonx.ai LLM calls."""

SIGNAL_EXPLANATION_PROMPT = """You are a pharmacovigilance assistant. Explain the following drug safety signal in 2-3 plain-language sentences for a regulatory affairs reviewer.

Drug: {drug}
Adverse event: {event}
Proportional Reporting Ratio (PRR): {prr:.2f}
Chi-squared: {chi2:.2f}
Number of co-occurring reports: {a}

Explanation:"""

CTD_GAP_SUMMARY_PROMPT = """You are a regulatory affairs assistant reviewing a CTD submission document. Summarize the following completeness gaps in 2-3 plain-language sentences, noting which missing sections are highest priority.

Missing sections:
{missing_sections}

Summary:"""
