"""Tests for prisma.stats correlation helpers."""
import math

import numpy as np
import pandas as pd
import pytest

from prisma.stats import (
    bootstrap_ci,
    correlation_table,
    fisher_ci,
    missingness_compare,
    partial_correlation,
)


@pytest.fixture
def df():
    rng = np.random.default_rng(7)
    n = 120
    x = rng.normal(size=n)
    y = 0.6 * x + rng.normal(scale=0.8, size=n)
    z = 0.5 * x + rng.normal(scale=0.9, size=n)
    g = ["A"] * 60 + ["B"] * 60
    d = pd.DataFrame({"x": x, "y": y, "z": z, "g": g})
    # introduce some missingness in y
    d.loc[d.index[:20], "y"] = np.nan
    return d


def test_fisher_ci_orders_and_bounds():
    lo, hi = fisher_ci(0.5, 100)
    assert lo < 0.5 < hi
    assert -1 <= lo <= 1 and -1 <= hi <= 1
    assert all(math.isnan(v) for v in fisher_ci(0.5, 3))  # n too small


def test_correlation_table_overall_and_grouped(df):
    t = correlation_table(df, "x", "y", group="g")
    assert set(["stratum", "n", "pearson_r", "ci_low", "ci_high", "spearman_rho"]).issubset(t.columns)
    assert t.iloc[0]["stratum"] == "ALL"
    assert {"A", "B"}.issubset(set(t["stratum"]))
    row = t.iloc[0]
    assert row["ci_low"] < row["pearson_r"] < row["ci_high"]
    assert row["pearson_r"] > 0  # positive by construction


def test_partial_correlation_reduces_when_confounded(df):
    p = partial_correlation(df, "x", "y", "z")
    assert p["n"] > 5
    assert abs(p["partial_r"]) <= abs(p["raw_r"]) + 1e-9  # controlling a correlate cannot inflate


def test_bootstrap_ci_brackets_point(df):
    b = bootstrap_ci(df, "x", "y", n_boot=500, seed=1)
    assert b["ci_low"] < b["r"] < b["ci_high"]


def test_missingness_compare_flags_columns(df):
    m = missingness_compare(df, indicator="y", by=["x", "z"])
    assert list(m["variable"]) == ["x", "z"]
    assert (m["n_missing"] == 20).all()
