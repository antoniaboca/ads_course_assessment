import os
import urllib.request
import zipfile
import pandas as pd
import geopandas as gpd
import yaml
from ipywidgets import interact_manual, Text, Password
import pymysql

from .config import *
from fynesse.access_scripts import sql, opm
from fynesse.access_scripts.schemas import GOV_COLUMNS, PP_DATA_SCHEMA, POSTCODE_DATA_SCHEMA, DATABASE_CREATE, PRICES_COORDINATES_DATA_SCHEMA

# This file accesses the data
def create_connection(user, password, host, database, port=3306):
        conn = None
        try:
            conn = pymysql.connect(user=user,
                                passwd=password,
                                host=host,
                                port=port,
                                local_infile=1,
                                db=database
                                )
        except Exception as e:
            print(f"Error connecting to the MariaDB Server: {e}")
        return conn

def read_credentials():
    with open("credentials.yaml") as file:
        credentials = yaml.safe_load(file)
    return credentials['username'], credentials['password']

def extract_file(file, extract_to):
        with zipfile.ZipFile(file) as zip_ref:
            zip_ref.extractall(extract_to)
        print(f'Extracted file into {extract_to}')

def request_url(url, save_to):
        urllib.request.urlretrieve(url, save_to)
        print(f'Saved file to {save_to}')

def create_database(conn):
        return sql.execute_query(conn, DATABASE_CREATE)

def create_pp_data(conn):
        rows = sql.execute_query(conn, PP_DATA_SCHEMA)
        return rows

def create_postcode_data(conn):
        rows = sql.execute_query(conn, POSTCODE_DATA_SCHEMA)
        return rows

def load_gov_data(conn, gov_url):
    for year in range(2021, 1930, -1):
        file = "pp-" + str(year) + ".csv"
        year_data = pd.DataFrame()
        try:
            print(gov_url + file)
            year_data = pd.read_csv(gov_url + file, header=None)
            year_data.columns = GOV_COLUMNS
        except:
            # we assume that if part data doesn't exist for year x, then it doesn't exist for x-1 
            break
        print('Found {} entries for year {}'.format(len(year_data), year))
        year_data.to_csv('gov.csv', index=False)
        sql.load_csv(conn, 'gov.uk', 'pp_data')
        print(f'Loaded {year} to SQL table `pp_data`')

def load_postcode_data(conn, postcode_url):
    request_url(postcode_url, './data/postcode.csv.zip')
    extract_file('./data/postcode.csv.zip', './data/postcode.csv')
    sql.load_csv(conn, './data/postcode.csv', 'postcode_data')

def load_london_wards(url):
    request_url(url, './data/london-wards.zip')
    extract_file('./data/london-wards.zip', './data/')

def region_data(conn, start_date, end_date, region_type, region_name):
    return sql.join_by_region(conn, start_date, end_date, region_type, region_name)

def box_data(conn, box, start_date, end_date, property_type):
    rows = sql.join_bounding_box(conn, box, start_date, end_date, property_type)
    sql.update_prices_coordinates_data(conn, rows)
    return sql.bounding_box_data(conn, box, start_date, end_date, property_type)

def pois_data(sample, tags, length=0.005):
    print(f'Loading all points from OpenStreetMap...')
    pois_df = opm.get_pois_stats(sample['longitude'], sample['latitude'], tags, length)
    print(f'Loaded all points.')
    return pois_df

def map_data(file):
    print(f'Reading map data from file {file}...')
    return gpd.read_file(file)
