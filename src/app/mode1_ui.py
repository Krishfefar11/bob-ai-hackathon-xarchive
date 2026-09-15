"""Mode 1 — Drug Safety Signal Detector tab."""
from components import RISK_EMOJI, RISK_HEX
from ingestion.openfda_client import fetch_faers_sample
from signal_detection.prr import calculate_prr
from signal_detection.signal_reporter import build_signal_report
import plotly.express as px
import streamlit as st

EXAMPLE_DRUGS = ["ASPIRIN", "IBUPROFEN", "METFORMIN", "WARFARIN"]


def render_signal_detector():
    st.subheader("Fetch adverse event reports and detect safety signals")

    if "drug_name" not in st.session_state:
        st.session_state.drug_name = "ASPIRIN"

    st.caption("Try:")
    quick_pick_clicked = False
    quick_cols = st.columns(len(EXAMPLE_DRUGS))
    for col, example in zip(quick_cols, EXAMPLE_DRUGS):
        if col.button(example, use_container_width=True):
            st.session_state.drug_name = example
            quick_pick_clicked = True

    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        drug_name = col1.text_input("Drug name", key="drug_name")
        n_records = col2.number_input("Reports to fetch", min_value=100, max_value=25000, value=1000, step=100)
        use_llm = col3.checkbox("LLM explanations (watsonx)", value=False)
        fetch_clicked = st.button("Fetch & Analyze", type="primary")

    # Cache the fetched/computed report in session_state — otherwise interacting with the
    # risk filter or download button below (each triggers its own rerun) would wipe the
    # results, since `fetch_clicked` is only True on the run where the button was pressed.
    if fetch_clicked or quick_pick_clicked:
        if not drug_name.strip():
            st.warning("Enter a drug name first.")
        else:
            with st.spinner(f"Fetching {n_records} OpenFDA reports for {drug_name}..."):
                df = fetch_faers_sample(drug_name.strip(), n=int(n_records))

            if df.empty:
                st.session_state.pop("mode1_result", None)
                st.error(
                    "No reports found for that drug name. Try a different spelling "
                    "(OpenFDA matches on the medicinalproduct text field)."
                )
            else:
                with st.spinner("Computing PRR / chi-squared..."):
                    prr_df = calculate_prr(df)
                    report = build_signal_report(prr_df, use_llm=use_llm)

                st.session_state["mode1_result"] = {
                    "report": report,
                    "queried_drug": drug_name.strip().upper(),
                    "reports_analyzed": int(df["report_id"].nunique()),
                }

    result = st.session_state.get("mode1_result")
    if result is not None:
        _render_results(result)


def _render_results(result):
    report = result["report"]
    queried_drug = result["queried_drug"]
    signals = report[report["signal"] & (report["drug"] == queried_drug)].sort_values("prr", ascending=False)

    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi1.metric("Reports analyzed", f"{result['reports_analyzed']:,}")
    kpi2.metric("Signals found", len(signals))
    kpi3.metric("Very high risk", int((signals["risk_level"] == "Very High").sum()) if not signals.empty else 0)
    kpi4.metric("Top PRR", f"{signals['prr'].max():.1f}" if not signals.empty else "—")

    if signals.empty:
        st.info(f"No pairs met the Evans et al. signal threshold for {queried_drug} in this sample.")
        return

    risk_filter = st.multiselect(
        "Filter by risk level",
        options=["Very High", "High", "Moderate"],
        default=["Very High", "High", "Moderate"],
    )
    filtered = signals[signals["risk_level"].isin(risk_filter)] if risk_filter else signals.iloc[0:0]

    if filtered.empty:
        st.info("No signals match the selected risk filter.")
        return

    display = filtered.head(50).copy()
    display["risk"] = display["risk_level"].map(lambda r: f"{RISK_EMOJI.get(r, '')} {r}")

    st.dataframe(
        display[["drug", "reaction", "a", "prr", "chi2", "risk", "explanation"]],
        column_config={
            "drug": "Drug",
            "reaction": "Reaction",
            "a": st.column_config.NumberColumn("Reports", format="%d"),
            "prr": st.column_config.ProgressColumn(
                "PRR", min_value=0.0, max_value=float(max(display["prr"].max(), 2.0)), format="%.2f"
            ),
            "chi2": st.column_config.NumberColumn("χ²", format="%.1f"),
            "risk": "Risk",
            "explanation": "Explanation",
        },
        use_container_width=True,
        hide_index=True,
    )

    st.download_button(
        "Download signals as CSV",
        filtered.drop(columns=["signal"]).to_csv(index=False),
        file_name=f"{queried_drug}_signals.csv",
        mime="text/csv",
    )

    top = filtered.head(15).sort_values("prr")
    fig = px.bar(
        top,
        x="prr",
        y="reaction",
        color="risk_level",
        color_discrete_map=RISK_HEX,
        orientation="h",
        labels={"prr": "PRR", "reaction": "", "risk_level": "Risk"},
        template="plotly_dark",
    )
    fig.update_layout(
        height=max(320, 28 * len(top)),
        margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend_title_text="Risk",
    )
    st.plotly_chart(fig, use_container_width=True)

    with st.expander(f"All {queried_drug} pairs (including non-signals)"):
        st.dataframe(report[report["drug"] == queried_drug], use_container_width=True, hide_index=True)

    with st.expander("Other primary-suspect drugs incidentally pulled into this sample"):
        st.caption(
            "These showed up because OpenFDA matched the search term anywhere on a report, "
            "not only as the primary suspect drug — shown for transparency, not part of the "
            f"{queried_drug} analysis above."
        )
        st.dataframe(report[report["drug"] != queried_drug], use_container_width=True, hide_index=True)
