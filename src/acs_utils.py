from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional, Sequence

import pandas as pd
import geopandas as gpd

#did this in R first, and translated into python

#  Bay Area county FIPS (CA) 
# These are widely used for Bay Area definitions (9-county).


BAY_AREA_COUNTY_FIPS = {
    "Alameda": "001",
    "Contra Costa": "013",
    "Marin": "041",
    "Napa": "055",
    "San Francisco": "075",
    "San Mateo": "081",
    "Santa Clara": "085",
    "Solano": "095",
    "Sonoma": "097",
}


def load_acs_csv(path: str | Path, year: Optional[int] = None) -> pd.DataFrame:
    """
    Load an ACS CSV that contains a GEOID column.
    Keeps GEOID as string (important—leading zeros).
    """
    df = pd.read_csv(path, dtype={"GEOID": "string"})
    if year is not None:
        df["year"] = year
    return df





#Here is the function that is being place into the notebook. 


def add_county_columns(acs_df: pd.DataFrame) -> pd.DataFrame:
    """
    Add county GEOID and county name derived from tract GEOID.
    """
    df = acs_df.copy()
    df["county_geoid"] = df["GEOID"].str[:5]

    county_fips_to_name = {
        "06001": "Alameda",
        "06013": "Contra Costa",
        "06075": "San Francisco",
        "06081": "San Mateo",
        "06085": "Santa Clara",
    }

    df["county_name"] = df["county_geoid"].map(county_fips_to_name)
    return df


def pop_weighted_mean(
    group: pd.DataFrame,
    value_col: str,
    weight_col: str = "total_pop",
) -> float:
    """
    Compute population-weighted mean for a group.
    """
    w = group[weight_col]
    v = group[value_col]
    return (v * w).sum() / w.sum()


def aggregate_tracts_to_county_year(acs_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate tract-level ACS data to county-year level.
    """
    return (
        acs_df.groupby(["county_geoid", "county_name", "year"])
        .apply(
            lambda g: pd.Series(
                {
                    "total_pop": g["total_pop"].sum(),
                    "median_home_value": pop_weighted_mean(g, "median_home_value"),
                    "median_income": pop_weighted_mean(g, "median_income"),
                    "pct_poc": pop_weighted_mean(g, "pct_poc"),
                }
            )
        )
        .reset_index()
    )
