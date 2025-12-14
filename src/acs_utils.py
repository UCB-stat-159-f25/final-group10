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


def clean_income_b19013_wide(df: pd.DataFrame, value_col: str = "B19013_001E") -> pd.DataFrame:
    """
    Mirror: income_clean <- transmute(GEOID, year, median_income = B19013_001E)
    Assumes 'wide' ACS table output where estimate col exists.
    """
    out = df[["GEOID", "year", value_col]].copy()
    out = out.rename(columns={value_col: "median_income"})
    return out


def clean_homevalue_b25077_wide(df: pd.DataFrame, value_col: str = "B25077_001E") -> pd.DataFrame:
    """
    Mirror: homvalue_clean <- transmute(GEOID, year, median_home_value = B25077_001E)
    """
    out = df[["GEOID", "year", value_col]].copy()
    out = out.rename(columns={value_col: "median_home_value"})
    return out


def clean_tenure_b25003_wide(
    df: pd.DataFrame,
    total_col: str = "B25003_001E",
    owner_col: str = "B25003_002E",
    renter_col: str = "B25003_003E",
) -> pd.DataFrame:
    """
    Mirror R:
      housing_units_total = B25003_001E
      owner_occupied      = B25003_002E
      renter_occupied     = B25003_003E
      homeownership_rate  = owner_occupied / housing_units_total
      renter_rate         = renter_occupied / housing_units_total
    """
    out = df[["GEOID", "year", total_col, owner_col, renter_col]].copy()
    out = out.rename(
        columns={
            total_col: "housing_units_total",
            owner_col: "owner_occupied",
            renter_col: "renter_occupied",
        }
    )

    # Avoid divide-by-zero
    denom = out["housing_units_total"].replace({0: pd.NA})
    out["homeownership_rate"] = out["owner_occupied"] / denom
    out["renter_rate"] = out["renter_occupied"] / denom
    return out


def fetch_ca_tracts(year: int) -> gpd.GeoDataFrame:
    """
    Download CA tract geometries from TIGER/Line for a given year.
    """
    # CA state FIPS is 06
    url = f"https://www2.census.gov/geo/tiger/TIGER{year}/TRACT/tl_{year}_06_tract.zip"
    gdf = gpd.read_file(url)
    # Ensure GEOID is string
    gdf["GEOID"] = gdf["GEOID"].astype("string")
    return gdf


def filter_bay_area_tracts(
    ca_tracts: gpd.GeoDataFrame,
    county_fips: Sequence[str] | None = None,
) -> gpd.GeoDataFrame:
    """
    Filter CA tracts down to Bay Area counties (by county FIPS).
    """
    if county_fips is None:
        county_fips = list(BAY_AREA_COUNTY_FIPS.values())

    out = ca_tracts[ca_tracts["COUNTYFP"].isin(county_fips)].copy()
    return out


def merge_acs_with_geometry(
    tracts_gdf: gpd.GeoDataFrame,
    acs_df: pd.DataFrame,
    on: str = "GEOID",
    how: str = "left",
) -> gpd.GeoDataFrame:
    """
    Mirror: bay_tracts %>% left_join(acs_2022, by="GEOID")
    """
    acs_df = acs_df.copy()
    acs_df[on] = acs_df[on].astype("string")
    tracts_gdf = tracts_gdf.copy()
    tracts_gdf[on] = tracts_gdf[on].astype("string")

    merged = tracts_gdf.merge(acs_df, on=on, how=how)
    return gpd.GeoDataFrame(merged, geometry="geometry", crs=tracts_gdf.crs)


def write_gpkg(
    gdf: gpd.GeoDataFrame,
    path: str | Path,
    layer: str,
) -> None:
    """
    Mirror: st_write(..., "xxx.gpkg", layer="...", delete_layer=TRUE)
    Note: geopandas will overwrite file; layer overwrite depends on driver behavior.
    Easiest reproducible behavior: write to a fresh file path.
    """
    path = Path(path)
    gdf.to_file(path, layer=layer, driver="GPKG")


def build_bay_area_gpkg_for_year(
    year: int,
    acs_df: pd.DataFrame,
    out_path: str | Path,
    layer: str,
) -> gpd.GeoDataFrame:
    """
    End-to-end convenience: fetch tracts -> filter Bay Area -> merge -> write gpkg.
    """
    ca_tracts = fetch_ca_tracts(year)
    bay_tracts = filter_bay_area_tracts(ca_tracts)
    merged = merge_acs_with_geometry(bay_tracts, acs_df)

    write_gpkg(merged, out_path, layer=layer)
    return merged


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
