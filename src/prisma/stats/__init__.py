"""Statistical helpers for transparent, reviewer-proof SLR / education-research analysis.

Reusable methods extracted while hardening the statistical rigour of the
20-60-20 AI-permitted-assessment study (Cuervo, 2026): within-stratum
correlations with Fisher-z confidence intervals, Spearman robustness,
partial correlation, bootstrap CIs for small cells, missingness/selection
checks, and a clustered (mixed-effects) model with ICC.
"""
from .correlations import (
    bootstrap_ci,
    correlation_table,
    fisher_ci,
    missingness_compare,
    mixed_model_icc,
    partial_correlation,
)

__all__ = [
    "bootstrap_ci",
    "correlation_table",
    "fisher_ci",
    "missingness_compare",
    "mixed_model_icc",
    "partial_correlation",
]
