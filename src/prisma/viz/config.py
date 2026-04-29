"""Matplotlib/seaborn config with Proportione brand palette.

Brand manual reference (private):
  Principal: #5F322F (corporate brown-red)
  Secondary: #551122, #3B431C, #6E8157, #566E30, #AEADB3
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import seaborn as sns

PALETTE = {
    "primary": "#5F322F",
    "secondary": "#551122",
    "accent_green": "#6E8157",
    "accent_olive": "#566E30",
    "accent_dark_green": "#3B431C",
    "neutral": "#AEADB3",
    "text": "#1F1410",
    "background": "#FFFFFF",
}

# Categorical palette for cluster plots, signal-KPI groups, etc.
SEQUENCE = [
    "#5F322F",  # primary
    "#6E8157",  # green
    "#551122",  # deep red
    "#566E30",  # olive
    "#3B431C",  # dark green
    "#AEADB3",  # neutral grey
]


def apply_style() -> None:
    """Apply the Proportione visual style to matplotlib globally."""
    sns.set_theme(style="whitegrid", context="paper")
    plt.rcParams.update(
        {
            "axes.edgecolor": PALETTE["text"],
            "axes.labelcolor": PALETTE["text"],
            "axes.titlecolor": PALETTE["text"],
            "axes.titleweight": "bold",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "xtick.color": PALETTE["text"],
            "ytick.color": PALETTE["text"],
            "text.color": PALETTE["text"],
            "figure.facecolor": PALETTE["background"],
            "axes.facecolor": PALETTE["background"],
            "savefig.facecolor": PALETTE["background"],
            "savefig.dpi": 150,
            "axes.prop_cycle": plt.cycler(color=SEQUENCE),
        }
    )
