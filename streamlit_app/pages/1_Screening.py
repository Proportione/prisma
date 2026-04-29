"""Streamlit page: title-abstract screening with a YAML rule set."""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd
import streamlit as st

from prisma.ingest.ris_io import get_field, parse_ris
from prisma.screening.engine import Decision, load_rules, screen_record

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEMO_RULES = REPO_ROOT / "examples" / "screening_rules_signal_kpi.yaml"

DEMO_RECORDS = [
    {
        "id": "doc-001",
        "title": "Forecasting hotel demand in Spain with Google Trends data",
        "abstract": "We use weekly search volume to forecast revenue and tourist arrivals using ARIMA-X.",
    },
    {
        "id": "doc-002",
        "title": "COVID-19 case prediction using Google search queries",
        "abstract": "Pandemic surveillance with online search data for hospital admissions.",
    },
    {
        "id": "doc-003",
        "title": "A systematic review of social media analytics for marketing",
        "abstract": "Bibliometric analysis of 200 papers on social media research.",
    },
    {
        "id": "doc-004",
        "title": "Predicting stock returns with Twitter sentiment",
        "abstract": "Empirical study using tweet volume and sentiment as predictors of S&P 500 returns. Random forest regression.",
    },
    {
        "id": "doc-005",
        "title": "Macroeconomic forecasting in Latin America",
        "abstract": "Traditional VAR model on quarterly GDP and inflation. No digital signals used.",
    },
]


st.set_page_config(page_title="Screening — PRISMA", page_icon="🔍", layout="wide")

st.markdown('<h1 style="color:#5F322F">Title-abstract screening</h1>', unsafe_allow_html=True)
st.write(
    "Two-tier rule engine — hard exclusions then multi-group positive inclusion. "
    "Every decision is traceable to the rule that fired."
)

with st.sidebar:
    st.subheader("Inputs")
    use_demo_rules = st.toggle("Use demo rules (Signal-KPI)", value=True)
    rules_file = (
        DEMO_RULES
        if use_demo_rules
        else st.file_uploader("Upload a YAML rule set", type=["yaml", "yml"])
    )

    use_demo_records = st.toggle("Use demo records", value=True)
    ris_upload = None
    if not use_demo_records:
        ris_upload = st.file_uploader("Upload a RIS corpus", type=["ris"])

if rules_file is None:
    st.warning("Provide a YAML rule set in the sidebar.")
    st.stop()

if isinstance(rules_file, Path):
    ruleset = load_rules(rules_file)
else:
    tmp = Path("/tmp") / "uploaded_rules.yaml"
    tmp.write_bytes(rules_file.getvalue())
    ruleset = load_rules(tmp)

# Build records list
records: list[dict[str, str]] = []
if use_demo_records:
    records = list(DEMO_RECORDS)
elif ris_upload is not None:
    tmp_ris = Path("/tmp") / "uploaded.ris"
    tmp_ris.write_bytes(ris_upload.getvalue())
    parsed = parse_ris(tmp_ris)
    for i, rec in enumerate(parsed):
        records.append(
            {
                "id": get_field(rec, "DO") or f"rec-{i:05d}",
                "title": get_field(rec, "TI") or get_field(rec, "T1"),
                "abstract": get_field(rec, "AB"),
            }
        )

if not records:
    st.warning("Provide records via the sidebar.")
    st.stop()

st.caption(f"**Rule set:** {ruleset.name} · **Records:** {len(records)}")

results = [screen_record(r["id"], r["title"], r["abstract"], ruleset) for r in records]

c1, c2, c3 = st.columns(3)
n_inc = sum(1 for r in results if r.decision == Decision.INCLUDE)
n_may = sum(1 for r in results if r.decision == Decision.MAYBE)
n_exc = sum(1 for r in results if r.decision == Decision.EXCLUDE)
c1.metric("Include", n_inc)
c2.metric("Maybe", n_may)
c3.metric("Exclude", n_exc)

table = pd.DataFrame(
    [
        {
            "id": r.record_id,
            "decision": r.decision.value,
            "title": r.title,
            "exclusion": "; ".join(rid for rid, _ in r.fired_exclusion),
            "fired_groups": "; ".join(g for g, fired in r.fired_inclusion.items() if fired),
            "missing_groups": "; ".join(r.missing_groups),
        }
        for r in results
    ]
)
st.dataframe(
    table,
    use_container_width=True,
    column_config={
        "decision": st.column_config.TextColumn(width="small"),
        "title": st.column_config.TextColumn(width="large"),
    },
)

with st.expander("Audit log (first matching snippets per rule)"):
    audit_rows = []
    for r in results:
        for rid, match in r.fired_exclusion:
            audit_rows.append({"id": r.record_id, "kind": "exclusion", "rule": rid, "match": match})
        for group, fired in r.fired_inclusion.items():
            for rid, match in fired:
                audit_rows.append({"id": r.record_id, "kind": f"inclusion:{group}", "rule": rid, "match": match})
    if audit_rows:
        st.dataframe(pd.DataFrame(audit_rows), use_container_width=True)
    else:
        st.info("No rules fired.")

# Download
buf = io.StringIO()
table.to_csv(buf, index=False)
st.download_button(
    "Download decisions CSV",
    data=buf.getvalue(),
    file_name="screening-decisions.csv",
    mime="text/csv",
)
