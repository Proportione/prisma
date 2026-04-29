"""Streamlit page: full-text extraction with a YAML taxonomy."""
from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from prisma.extraction.patterns import extract_record, load_taxonomy
from prisma.extraction.pdf_text import extract_pdf_text

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DEMO_TAXONOMY = REPO_ROOT / "examples" / "extraction_taxonomy_signal_kpi.yaml"

DEMO_TEXT = """
Abstract. The aim of this study is to forecast monthly hotel revenue per
available room (RevPAR) in Spain using Google Trends search volume.

Methodology. We collected weekly Google Trends data for tourism-related
queries in Spain from 2010 to 2022. The dependent variable is hotel revenue
from the National Statistics Institute. We employ an ARIMA-X regression
model with train/test split.

Results. The coefficient on Google Trends search volume is positive and
statistically significant (p < 0.001), with R² = 0.84. Our findings
suggest a positive effect of digital signals on tourist demand
forecasting. TripAdvisor reviews provide secondary information.
"""

st.set_page_config(page_title="Extraction — PRISMA", page_icon="📄", layout="wide")

st.markdown('<h1 style="color:#5F322F">Full-text extraction</h1>', unsafe_allow_html=True)
st.write(
    "PyMuPDF text extraction + taxonomy-driven field extraction. "
    "Define your taxonomy in YAML; the engine returns structured data with audit snippets."
)

with st.sidebar:
    st.subheader("Inputs")
    use_demo_taxonomy = st.toggle("Use demo taxonomy (Signal-KPI)", value=True)
    if use_demo_taxonomy:
        taxonomy_file: Path | None = DEMO_TAXONOMY
    else:
        upload = st.file_uploader("Upload taxonomy YAML", type=["yaml", "yml"])
        taxonomy_file = None
        if upload:
            tmp = Path("/tmp") / "uploaded_taxonomy.yaml"
            tmp.write_bytes(upload.getvalue())
            taxonomy_file = tmp

    st.divider()
    source = st.radio("Source", ["Demo abstract", "Upload PDF"])
    pdf_path = None
    if source == "Upload PDF":
        pdf_upload = st.file_uploader("PDF file", type=["pdf"])
        if pdf_upload:
            pdf_path = Path("/tmp") / "uploaded.pdf"
            pdf_path.write_bytes(pdf_upload.getvalue())

if taxonomy_file is None:
    st.warning("Provide a taxonomy YAML in the sidebar.")
    st.stop()

tax = load_taxonomy(taxonomy_file)

if source == "Demo abstract":
    text = DEMO_TEXT
elif pdf_path is not None:
    pages = extract_pdf_text(pdf_path, max_pages=30)
    text = "\n".join(p.text for p in pages)
else:
    st.info("Upload a PDF to extract.")
    st.stop()

with st.expander("Show input text", expanded=(source == "Demo abstract")):
    st.text(text[:3000] + ("…" if len(text) > 3000 else ""))

result = extract_record(text, tax)
audit = result.pop("_audit", {})

st.subheader(f"Extracted fields — taxonomy '{tax.name}'")

rows = []
for fname, value in result.items():
    rows.append(
        {
            "field": fname,
            "value": ", ".join(value) if isinstance(value, list) else (value or "—"),
            "n_hits": len(audit.get(fname, [])),
        }
    )
st.dataframe(pd.DataFrame(rows), use_container_width=True)

with st.expander("Snippets (audit trail)"):
    for fname, hits in audit.items():
        if not hits:
            continue
        st.markdown(f"**{fname}**")
        for h in hits[:5]:
            st.caption(f"› [{h.label}] …{h.snippet.strip()}…")
