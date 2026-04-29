"""Streamlit page: MMAT 2018 quality assessment."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from prisma.extraction.pdf_text import extract_pdf_text
from prisma.quality.mmat import (
    MMAT_DESCRIPTIVE_HEURISTICS,
    QualityLevel,
    assess_text,
)

st.set_page_config(page_title="MMAT — PRISMA", page_icon="🔬", layout="wide")

DEMO_TEXTS = {
    "Strong empirical study (Pub 3 style)": """
The aim of this study is to forecast monthly hotel revenue using Google
Trends. We collected weekly data from 2010 to 2022 (n = 624 observations).
This study employs an ARIMA-X regression with train/test split. Independent
variables include search volume; dependent variable is sales. Results section
shows that the coefficient on search volume is statistically significant
(p < 0.001), R² = 0.84. Our findings suggest that digital signals improve
forecast accuracy. Limitations: small geographic scope.
""",
    "Mixed-quality conference paper": """
We explore the relation between Google searches and tourism in Spain.
We use monthly data and a regression model. Some results are reported
in Table 1.
""",
    "Editorial / non-empirical note": """
Digital trace data is increasingly important for business intelligence.
Practitioners should consider these signals when planning marketing.
""",
}

st.markdown('<h1 style="color:#5F322F">Quality assessment — MMAT 2018</h1>', unsafe_allow_html=True)
st.write(
    "Hong et al. (2018) **Mixed Methods Appraisal Tool**, quantitative-descriptive "
    "criteria. Heuristic auto-scoring; final decisions need human review."
)

with st.sidebar:
    source = st.radio("Source", ["Demo text", "Upload PDF"])
    if source == "Demo text":
        sample_name = st.selectbox("Demo sample", list(DEMO_TEXTS.keys()))
        text = DEMO_TEXTS[sample_name]
        record_id = sample_name
    else:
        upload = st.file_uploader("PDF file", type=["pdf"])
        if upload:
            tmp = Path("/tmp") / "uploaded_mmat.pdf"
            tmp.write_bytes(upload.getvalue())
            pages = extract_pdf_text(tmp, max_pages=30)
            text = "\n".join(p.text for p in pages)
            record_id = upload.name
        else:
            text = ""
            record_id = ""

if not text:
    st.info("Pick a demo or upload a PDF.")
    st.stop()

a = assess_text(record_id, text)

c1, c2, c3 = st.columns([1, 1, 2])
c1.metric("Total score", f"{a.total:.1f} / 5")
c2.metric("Quality level", a.level.value)

# Color-coded badge for the level
color = {
    QualityLevel.HIGH: "#566E30",
    QualityLevel.MEDIUM: "#5F322F",
    QualityLevel.LOW: "#551122",
}[a.level]
c3.markdown(
    f"<div style='background:{color};color:white;padding:8px 14px;"
    f"border-radius:6px;display:inline-block;font-weight:600;'>"
    f"{a.level.value}</div>",
    unsafe_allow_html=True,
)

st.subheader("Per-criterion assessment")
rows = []
for crit in MMAT_DESCRIPTIVE_HEURISTICS:
    rows.append(
        {
            "criterion": crit.code,
            "question": crit.question,
            "score": a.scores[crit.code].value,
            "n_indicators_matched": len(a.matched[crit.code]),
        }
    )
st.dataframe(pd.DataFrame(rows), use_container_width=True)

with st.expander("Matched indicators (audit)"):
    for crit in MMAT_DESCRIPTIVE_HEURISTICS:
        matched = a.matched[crit.code]
        if matched:
            st.markdown(f"**{crit.code}** — {crit.question}")
            for m in matched[:6]:
                st.caption(f"› {m}")

st.caption(
    "MMAT 2018 — Hong, Q.N., et al. (2018). *Education for Information* 34:285-291. "
    "https://doi.org/10.3233/EFI-180221"
)
