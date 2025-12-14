import geopandas as gpd
import pandas as pd
from pathlib import Path

# Disclaimer: 
# these functions were orginially created in R,
# there are some workarounds that had to be used
# so that we could get similar functionality in Python.

# to create GeoPackage (to be able to map info of Bay Area using ACS Census)
def create_ba_acs_gpkg(acs_csv_path, 
                       output_path = "data/acs_bayarea_2022_with_geometry.gpkg",
                       year  = 2022):
    """ Load CA 2020 census tracts, filter by Bay Area,
    join ACS 2022 data, and write a GeoPackage output.

    Input: 
        acs_csv_path (str, path ACS file)
        output_path (str, for the GeoPackage)
        year (int, year to filter by)
    Output: Geopackage file """

    # ACS Census
    ca_tracts_url = (
        "https://www2.census.gov/geo/tiger/TIGER2020/TRACT/tl_2020_06_tract.zip"
    )
    ca_tracts = gpd.read_file(ca_tracts_url)

    # Federal Information Processing Series for
    # Alameda, Contra Costa, SF, San Mateo, Santa Clara
    # these are unique ids for geographic regions in US
    bay_fips = ["001", "013", "075", "081", "085"]

    # geographic areas within counties
    bay_tracts = ca_tracts[ca_tracts["COUNTYFP"].isin(bay_fips)]
    bay_tracts = bay_tracts[["GEOID", "NAME", "geometry"]]

    # ACS CSV data file
    acs = pd.read_csv(acs_csv_path)

    # name of layer using year
    layer_name = f"acs_{year}"
    
    # filter for year only
    acs_year = acs[acs["year"] == year].copy()

    # merge bay data with filtered ACS
    bay_tracts_acs = bay_tracts.merge(acs_year, on="GEOID", how="left")

    # create gpkg
    bay_tracts_acs.to_file(output_path,
                            layer=layer_name,
                            driver="GPKG")

    return bay_tracts_acs

# to pre-process HOLC data

def load_acs_census_ca():
    counties = gpd.read_file(
        "https://www2.census.gov/geo/tiger/GENZ2022/shp/"
        "cb_2022_us_county_500k.zip")
    
    counties = counties[counties["STATEFP"] == "06"]
    
    return counties
    
def holc_data(path_raw_file):

    """ To process and filter Mapping Inequality's data
    and return the dataset we use for Redlining in Bay Area.
    Input: original dataset path (str)
    Output: json file filtered by bay area counties"""

    outpath = "holc_bayarea.json"
    
    # read/load data files
    holc = gpd.read_file(path_raw_file)
    counties = load_acs_census_ca()

    # to create valid polygons
    holc = holc.set_geometry(holc.geometry.buffer(0))
    
    # filter to California
    holc_ca = holc[holc["state"] == "CA"].copy()

    # match crs for spatial join
    counties = counties.to_crs(holc_ca.crs)
    holc_by_county = gpd.sjoin(holc_ca, counties, predicate="intersects")

    # filter to bay_area counties
    bay_list = [
        "Alameda County",
        "Contra Costa County",
        "San Francisco County",
        "San Mateo County",
        "Santa Clara County"
    ]
    holc_bayarea = holc_by_county[holc_by_county["NAMELSAD"].isin(bay_list)].copy()

    holc_bayarea.to_file(outpath, driver="GeoJSON")
