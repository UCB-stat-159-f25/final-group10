from pathlib import Path
import geopandas as gpd
import pandas as pd
from src.data_preprocessing import *

def get_data_file(data_filename):
    
    """ Read data file using geopandas.
        
        Input: Data file name (str)
        Output: Geopandas Dataframe"""
    
    cwd_path = Path.cwd()
    holc = gpd.read_file(Path.cwd()/data_filename)

    return holc

def get_bay_counties(correct_crs):

    """ Get Bay Area counties outline, 
    based on provided FIPS and State
    
    Input: Coordinate Reference System to match data
    Output: Geopandas Dataframe"""

    # get census file
    counties = load_acs_census_ca()
    # Federal Information Processing Series for
    # Alameda, Contra Costa, SF, San Mateo, Santa Clara
    # these are unique ids for geographic regions in US
    bay_fips = ["001", "013", "075", "081", "085"]
    
    # get only counties for FIPS
    bay_outline = counties[counties["COUNTYFP"].isin(bay_fips)]
    
    # match crs to our data
    bay_outline = bay_outline.to_crs(correct_crs)

    return bay_outline