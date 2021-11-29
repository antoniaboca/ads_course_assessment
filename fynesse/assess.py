import pandas as pd
import geopandas as gpd
from geopandas.tools import sjoin
import numpy as np
import matplotlib.pyplot as plt

from .config import *

import fynesse.access as access
from fynesse.access_scripts import opm, sql, schemas
"""These are the types of import we might expect in this file
import pandas
import bokeh
import matplotlib.pyplot as plt
import sklearn.decomposition as decomposition
import sklearn.feature_extraction"""

"""Place commands in this file to assess the data you have downloaded. How are missing values encoded, how are outliers encoded? What do columns represent, makes rure they are correctly labeled. How is the data indexed. Crete visualisation routines to assess the data (e.g. in bokeh). Ensure that date formats are correct and correctly timezoned."""

def assess_region(conn, start_date, end_date, region_type, region_name):
    """Load the data from access and ensure missing values are correctly encoded as well as indices correct, column names informative, date and times correctly formatted. Return a structured data structure such as a data frame."""
    print('Loading data from the sql database...')
    region = access.region_data(conn, start_date, end_date, region_type, region_name)
    print(f'Loaded {region} from the database. Assessing...')
    required_columns = ['price', 'latitude', 'longitude', 'postcode', 'postcode_area', 'postcode_district']
    try: 
        for col in required_columns:
            assert not region[col].isnull().any()

        assert pd.to_numeric(region['price'], errors='coerce').notnull().all()

        prop_types = ['D', 'S', 'T', 'F', 'O']
        for uniq in region['property_type'].unique():
            assert uniq in prop_types
        
    except Exception as e:
        print(f'The following exception has arised when checking data: \n{e}')
    print('Assessment is finished.')
    return region

def assess_pois(sample, tags):
    print(f'Loading pois for given sample...')
    pois_df = opm.get_pois_stats(sample['longitude'], sample['latitude'], tags)
    print(f'Loaded all points. Computing stats...')
    for tag in tags.keys():
        pois_df[tag] = pois_df[tag].fillna(0)
        assert pd.to_numeric(pois_df[tag], errors='coerce').notnull().any()

    pois_df['total_pois'] = pois_df[list(tags.keys())].sum(axis=1)
    print(f'Stats computed.')
    return pois_df


def query_map(region, region_map):
    geometry = gpd.points_from_xy(region.longitude, region.latitude)
    region_gdf = gpd.GeoDataFrame(region, geometry=geometry)
    region_gdf.crs = 'EPSG:4326'
    map_df = access.map_data(region_map).to_crs('EPSG:4326')

    region_joined = sjoin(region_gdf, map_df, how='left')

    return region_joined, map_df


def show_average_map(region_joined, map_df, group_col='NAME', avg_column='price', log_scale=True, figsize=(20,15)):
    if log_scale:
        log_joined = region_joined.copy()
        log_joined[avg_column] = np.log(log_joined[avg_column])
        region_joined = log_joined

    grouped = region_joined.groupby(group_col)[avg_column].mean()
    avg_val = map_df.join(grouped, on=group_col)
    fig, ax = plt.subplots()
    w, h = figsize
    fig.set_size_inches(w=w, h=h)
    ax.set_title(f"Average {'log scale ' if log_scale else ''}{avg_column} in the region.")
    avg_val.plot(column=avg_column, ax=ax, legend=True)

def show_boxplot(data, column='price', grouped=None, log_scale=True, figsize=(8,10)):
    values = data.copy()
    if log_scale:
        values[column] = np.log(values[column])
    if grouped is not None:
        values = values.groupby(grouped)
    values.boxplot(column=column, figsize=figsize, subplots=False)

def show_average_bar(data, avg_column='price', group_by='postcode_area'):
    grouped = data.groupby(group_by)[avg_column].mean()
    fig, ax = plt.subplots()
    fig.set_size_inches(w=8, h=6)
    ax.set_title(f'Average {avg_column} grouped by {group_by}')
    grouped.plot(kind='bar', ax=ax)

def get_price_correlation(sample, pois_df, tags):
    corrs = {}
    for tag in tags.keys():
        corrs[tag] = sample['price'].corr(pois_df[tag])
    return corrs

def query(data):
    """Request user input for some aspect of the data."""
    raise NotImplementedError

def view(data):
    """Provide a view of the data that allows the user to verify some aspect of its quality."""
    raise NotImplementedError

def labelled(data):
    """Provide a labelled set of data ready for supervised learning."""
    raise NotImplementedError
