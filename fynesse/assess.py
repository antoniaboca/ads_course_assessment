import pandas as pd
import geopandas as gpd
from geopandas.tools import sjoin
import numpy as np
import matplotlib.pyplot as plt

from .config import *

import fynesse.access as access

def assess_houses(region):
    print(f'Assessing dataframe...')
    required_columns = ['price', 'date_of_transfer', 'property_type', 'latitude', 'longitude', 'postcode']
    try: 
        for col in required_columns:
            assert not region[col].isnull().any()

        assert pd.to_numeric(region['price'], errors='coerce').notnull().all()

        prop_types = ['D', 'S', 'T', 'F', 'O']
        for uniq in region['property_type'].unique():
            assert uniq in prop_types
        
    except Exception as e:
        raise e
    print('Assessment is finished.')
    return region

def assess_pois(pois_df, tags):
    print(f'Assess pois and compute total pois...')
    for tag in tags.keys():
        assert tag in pois_df.columns
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


def draw_correlation(x, y):
  plt.scatter(x, y)
  axes = plt.gca()
  m, b = np.polyfit(x, y, 1)
  x_plot = np.linspace(axes.get_xlim()[0], axes.get_xlim()[1], 100)
  plt.plot(x_plot, m * x_plot + b, '-')

def get_box(latitude, longitude, len_lat, len_long):
    south, north = latitude - len_lat, latitude + len_lat
    west, east = longitude - len_long, longitude + len_long
    return (north, south, west, east)