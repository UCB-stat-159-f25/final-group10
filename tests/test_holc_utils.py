import geopandas as gpd
from pathlib import Path
from src.holc_utils import *

def test_get_data_file():
    
    # json file for testing
    geojson_file = "../data/holc_bayarea.json"

    gdf = get_data_file(geojson_file)

    assert isinstance(gdf, gpd.GeoDataFrame)
    assert not gdf.empty
    assert "geometry" in gdf.columns

def test_get_bay_counties():
    
    # crs for testing
    correct_crs = "EPSG:3857"

    bay_counties = get_bay_counties(correct_crs)

    assert isinstance(bay_counties, gpd.GeoDataFrame)
    assert len(bay_counties) == 5
    assert bay_counties.crs.to_string() == correct_crs
