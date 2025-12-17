import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

from src.acs_utils import (
    clean_homevalue_b25077_wide,
    clean_tenure_b25003_wide,
    merge_acs_with_geometry,
)


def test_clean_homevalue_renames_column_and_keeps_keys():
    df = pd.DataFrame(
        {
            "GEOID": ["06075010100", "06075010200"],
            "year": [2020, 2020],
            "B25077_001E": [900000, 1100000],
        }
    )
    out = clean_homevalue_b25077_wide(df)

    assert list(out.columns) == ["GEOID", "year", "median_home_value"]
    assert out["median_home_value"].iloc[0] == 900000


def test_clean_tenure_computes_rates():
    df = pd.DataFrame(
        {
            "GEOID": ["06075010100"],
            "year": [2020],
            "B25003_001E": [100],  # total
            "B25003_002E": [60],   # owner
            "B25003_003E": [40],   # renter
        }
    )
    out = clean_tenure_b25003_wide(df)

    assert out.loc[0, "homeownership_rate"] == 0.60
    assert out.loc[0, "renter_rate"] == 0.40


def test_merge_acs_with_geometry_preserves_geometry_and_crs():
    tracts = gpd.GeoDataFrame(
        {"GEOID": ["06075010100"], "geometry": [Point(0, 0)]},
        crs="EPSG:4326",
    )
    acs = pd.DataFrame(
        {"GEOID": ["06075010100"], "year": [2020], "median_home_value": [900000]}
    )

    merged = merge_acs_with_geometry(tracts, acs)

    assert isinstance(merged, gpd.GeoDataFrame)
    assert merged.crs.to_string() == "EPSG:4326"
    assert merged.loc[0, "median_home_value"] == 900000
    assert merged.geometry.iloc[0].equals(Point(0, 0))
