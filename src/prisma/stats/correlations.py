"""Correlation and robustness statistics for education / SLR datasets.

Design goals: every estimate ships with the information a sceptical reviewer
asks for — sample size, a confidence interval, a rank-based robustness check,
and (where relevant) controls for mechanical overlap, small-cell fragility,
selection bias and clustering. Pure functions over pandas DataFrames.
"""
from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
import pandas as pd
from scipy import stats


def fisher_ci(r: float, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Fisher z-transform confidence interval for a Pearson correlation.

    Returns (nan, nan) when undefined (n < 4 or |r| >= 1).
    """
    if n < 4 or abs(r) >= 1.0:
        return (float("nan"), float("nan"))
    z = math.atanh(r)
    se = 1.0 / math.sqrt(n - 3)
    crit = stats.norm.ppf(1 - alpha / 2)
    return (math.tanh(z - crit * se), math.tanh(z + crit * se))


def _pair(df: pd.DataFrame, x: str, y: str) -> pd.DataFrame:
    return df[[x, y]].apply(pd.to_numeric, errors="coerce").dropna()


def correlation_table(
    df: pd.DataFrame,
    x: str,
    y: str,
    group: str | None = None,
    alpha: float = 0.05,
) -> pd.DataFrame:
    """Pearson r (+ Fisher-z CI) and Spearman rho with n, overall and per group.

    The Spearman column is the headline robustness check: a Pearson/Spearman gap
    flags outlier- or spread-driven associations.
    """
    def one(sub: pd.DataFrame, label: str) -> dict | None:
        d = _pair(sub, x, y)
        if len(d) < 4:
            return None
        pr, pp = stats.pearsonr(d[x], d[y])
        sr, sp = stats.spearmanr(d[x], d[y])
        lo, hi = fisher_ci(pr, len(d), alpha)
        return {
            "stratum": label, "n": len(d),
            "pearson_r": round(pr, 3), "ci_low": round(lo, 3), "ci_high": round(hi, 3),
            "pearson_p": pp, "spearman_rho": round(sr, 3), "spearman_p": sp,
        }

    rows = [one(df, "ALL")]
    if group is not None:
        for g, sub in df.groupby(group):
            rows.append(one(sub, str(g)))
    return pd.DataFrame([r for r in rows if r is not None])


def partial_correlation(df: pd.DataFrame, x: str, y: str, covar: str) -> dict:
    """First-order partial correlation r(x, y | covar).

    Answers 'does the x-y association survive controlling for a confounder
    such as general ability?'.
    """
    d = df[[x, y, covar]].apply(pd.to_numeric, errors="coerce").dropna()
    if len(d) < 5:
        return {"n": len(d), "partial_r": float("nan"), "raw_r": float("nan")}
    rxy = stats.pearsonr(d[x], d[y])[0]
    rxz = stats.pearsonr(d[x], d[covar])[0]
    ryz = stats.pearsonr(d[y], d[covar])[0]
    denom = math.sqrt((1 - rxz ** 2) * (1 - ryz ** 2))
    pr = (rxy - rxz * ryz) / denom if denom else float("nan")
    return {"n": len(d), "partial_r": round(pr, 3), "raw_r": round(rxy, 3)}


def bootstrap_ci(
    df: pd.DataFrame, x: str, y: str, n_boot: int = 5000, seed: int = 0, alpha: float = 0.05
) -> dict:
    """Percentile bootstrap CI for a Pearson r — for small/fragile cells."""
    d = _pair(df, x, y)
    if len(d) < 10:
        return {"n": len(d), "r": float("nan"), "ci_low": float("nan"), "ci_high": float("nan")}
    arr = d.to_numpy()
    rng = np.random.default_rng(seed)
    boot = []
    for _ in range(n_boot):
        s = arr[rng.integers(0, len(arr), len(arr))]
        if s[:, 0].std() > 0 and s[:, 1].std() > 0:
            boot.append(np.corrcoef(s[:, 0], s[:, 1])[0, 1])
    return {
        "n": len(d), "r": round(float(np.corrcoef(arr[:, 0], arr[:, 1])[0, 1]), 3),
        "ci_low": round(float(np.percentile(boot, 100 * alpha / 2)), 3),
        "ci_high": round(float(np.percentile(boot, 100 * (1 - alpha / 2))), 3),
        "n_boot": len(boot),
    }


def missingness_compare(df: pd.DataFrame, indicator: str, by: Sequence[str]) -> pd.DataFrame:
    """Compare rows where `indicator` is present vs missing on `by` variables.

    Surfaces selection bias from listwise deletion (Mann-Whitney U, non-parametric).
    """
    present = df[df[indicator].notna()]
    missing = df[df[indicator].isna()]
    out = []
    for var in by:
        h = pd.to_numeric(present[var], errors="coerce").dropna()
        m = pd.to_numeric(missing[var], errors="coerce").dropna()
        rec = {"variable": var, "n_present": len(h), "n_missing": len(m),
               "mean_present": round(h.mean(), 2) if len(h) else float("nan"),
               "mean_missing": round(m.mean(), 2) if len(m) else float("nan"), "mw_p": float("nan")}
        if len(h) > 3 and len(m) > 3:
            rec["mw_p"] = stats.mannwhitneyu(h, m).pvalue
        out.append(rec)
    return pd.DataFrame(out)


def mixed_model_icc(df: pd.DataFrame, outcome: str, predictor: str, group: str) -> dict:
    """Random-intercept mixed model `outcome ~ predictor + (1|group)` with ICC.

    Accounts for clustering (students nested in cohorts/courses). Reports the
    cluster-adjusted fixed effect, the naive OLS effect, and the intraclass
    correlation. Requires the optional `statsmodels` dependency.
    """
    try:
        import statsmodels.formula.api as smf
    except ImportError as exc:  # pragma: no cover
        raise ImportError(
            "mixed_model_icc requires statsmodels: pip install 'proportione-prisma[stats]'"
        ) from exc
    d = df[[outcome, predictor, group]].apply(
        lambda c: pd.to_numeric(c, errors="coerce") if c.name != group else c
    ).dropna()
    md = smf.mixedlm(f"{outcome} ~ {predictor}", d, groups=d[group]).fit(reml=False)
    ols = smf.ols(f"{outcome} ~ {predictor}", d).fit()
    gv = float(md.cov_re.iloc[0, 0])
    rv = float(md.scale)
    icc = gv / (gv + rv) if (gv + rv) else float("nan")
    return {
        "n": len(d), "n_groups": int(d[group].nunique()),
        "coef": round(float(md.params.get(predictor)), 4), "p": float(md.pvalues.get(predictor)),
        "icc": round(icc, 3),
        "ols_coef": round(float(ols.params[predictor]), 4), "ols_p": float(ols.pvalues[predictor]),
    }
