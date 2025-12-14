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