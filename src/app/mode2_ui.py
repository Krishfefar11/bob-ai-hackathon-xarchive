"""Mode 2 — Regulatory Submission Readiness Checker tab."""
from submission_checker.gap_analyzer import analyze_document
import pandas as pd
import plotly.graph_objects as go
import streamlit as st


def render_submission_checker():
    st.subheader("Check a draft regulatory document against the ICH M4 CTD structure")

    uploaded = st.file_uploader("Upload a CTD module document", type=["pdf", "docx", "txt"])

    if uploaded is None:
        st.info("Upload a PDF, DOCX, or TXT file to check its structure against ICH M4.")
        return

    with st.spinner("Parsing document and checking CTD structure..."):
        try:
            result = analyze_document(uploaded, uploaded.name)
        except ValueError as exc:
            st.error(str(exc))
            return

    overview, gauge = st.columns([3, 1])
    with overview:
        st.metric(
            "Overall completeness",
            f"{result['completeness_pct']}%",
            f"{result['present_count']}/{result['total_count']} sections",
        )
        st.progress(result["completeness_pct"] / 100)
    with gauge:
        st.plotly_chart(
            _completeness_donut(result["completeness_pct"], result["present_count"], result["total_count"]),
            use_container_width=True,
            config={"staticPlot": True},
        )

    st.caption("Completeness per module")
    module_cols = st.columns(len(result["modules"]))
    for col, (module, info) in zip(module_cols, result["modules"].items()):
        with col, st.container(border=True):
            st.caption(module)
            st.markdown(f"### {info['completeness_pct']:.0f}%")
            st.progress(info["completeness_pct"] / 100)
            st.caption(f"{info['present_count']}/{info['total_count']} sections")

    for module, info in result["modules"].items():
        with st.expander(f"{module} — {info['title']} ({info['completeness_pct']:.0f}%)"):
            for number, sec in info["sections"].items():
                icon = "✅" if sec["present"] else "❌"
                st.write(f"{icon} **{number}** {sec['title']}")

    if result["missing_sections"]:
        st.markdown("**Missing sections**")
        st.dataframe(
            pd.DataFrame({"Missing section": result["missing_sections"]}),
            use_container_width=True,
            hide_index=True,
        )
        st.download_button(
            "Download gap report",
            _gap_report_text(uploaded.name, result),
            file_name=f"{uploaded.name}_gap_report.txt",
        )
    else:
        st.success("All CTD sections detected.")


def _completeness_donut(pct: float, present: int, total: int) -> go.Figure:
    fig = go.Figure(
        go.Pie(
            values=[present, max(total - present, 0)],
            labels=["Present", "Missing"],
            hole=0.72,
            marker_colors=["#14B8A6", "#374151"],
            textinfo="none",
            sort=False,
        )
    )
    fig.update_layout(
        showlegend=False,
        height=160,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor="rgba(0,0,0,0)",
        annotations=[dict(text=f"{pct:.0f}%", x=0.5, y=0.5, font_size=22, showarrow=False)],
    )
    return fig


def _gap_report_text(filename: str, result: dict) -> str:
    lines = [
        f"CTD Gap Report — {filename}",
        f"Overall completeness: {result['completeness_pct']}% "
        f"({result['present_count']}/{result['total_count']} sections)",
        "",
        "Completeness per module:",
    ]
    for module, info in result["modules"].items():
        lines.append(f"- {module}: {info['completeness_pct']}% ({info['present_count']}/{info['total_count']})")
    lines += ["", "Missing sections:"] + [f"- {m}" for m in result["missing_sections"]]
    return "\n".join(lines)
