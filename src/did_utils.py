import pandas as pd
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pandas as pd
import matplotlib.pyplot as plt


def prepare_did_data(
    df: pd.DataFrame,
    treat_counties: list[str],
    outcome_col: str,
    policy_year: int,
) -> pd.DataFrame:
    """
    Prepare data for difference-in-differences analysis.

    Parameters
    ----------
    df : DataFrame
        County-year data
    treat_counties : list of str
        Counties considered treated (e.g., high redlining exposure)
    outcome_col : str
        Outcome variable (e.g., median_home_value)
    policy_year : int
        Policy cutoff year

    Returns
    -------
    DataFrame with treat, post, and treat_post indicators
    """
    out = df.copy()

    out["treat"] = out["county_name"].isin(treat_counties).astype(int)
    out["post"] = (out["year"] >= policy_year).astype(int)
    out["treat_post"] = out["treat"] * out["post"]

    return out





def plot_parallel_trends(
    did_df: pd.DataFrame,
    outcome_col: str,
    policy_year: int,
    year_col: str = "year",
    treat_col: str = "treat",
    agg: str = "mean",
    title: Optional[str] = None,
):
    """
    Plot average outcome over time for treated vs control groups (parallel trends check).

    Expects did_df to contain:
      - year_col (e.g. "year")
      - treat_col (0/1)
      - outcome_col (numeric)

    Returns (fig, ax).
    """
    if agg not in {"mean", "median"}:
        raise ValueError("agg must be 'mean' or 'median'")

    grouped = (
        did_df.groupby([year_col, treat_col])[outcome_col]
        .agg(agg)
        .reset_index()
        .sort_values(year_col)
    )

    fig, ax = plt.subplots(figsize=(8, 5))

    for t_value, label in [(0, "Control"), (1, "Treated")]:
        sub = grouped[grouped[treat_col] == t_value]
        ax.plot(sub[year_col], sub[outcome_col], label=label)

    ax.axvline(policy_year, linestyle="--")
    ax.set_xlabel("Year")
    ax.set_ylabel(outcome_col.replace("_", " ").title())
    ax.set_title(title or f"Parallel Trends Check: {outcome_col} (policy year = {policy_year})")
    ax.legend()
    ax.grid(True, linestyle="--", alpha=0.5)

    return fig, ax

