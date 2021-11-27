import os
import urllib.request
import zipfile
import pandas as pd
import geopandas as gpd
import yaml
from ipywidgets import interact_manual, Text, Password

from .config import *
from fynesse.access_scripts import sql
from fynesse.access_scripts.schemas import GOV_COLUMNS, PP_DATA_SCHEMA, POSTCODE_DATA_SCHEMA, DATABASE_CREATE

# This file accesses the data

@interact_manual(username=Text(description="Username:"), 
                 password=Password(description="Password:"))
def write_credentials(username, password):
    with open("credentials.yaml", "w") as file:
        credentials_dict = {'username': username, 
                            'password': password}
        yaml.dump(credentials_dict, file)

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
        query = PP_DATA_SCHEMA + sql.primary_key_query('property_prices', 'pp_data')
        rows = sql.execute_query(conn, query)
        return rows

def create_postcode_data(conn):
        query = POSTCODE_DATA_SCHEMA + sql.primary_key_query('property_prices', 'pp_data')
        rows = sql.execute_query(conn, query)
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
            year_data.to_csv('gov.csv')
            sql.load_csv_to_sql(conn, 'gov.uk', 'pp_data')
            print(f'Loaded {year} to SQL table `pp_data`')

def load_postcode_data(postcode_url):
    request_url(postcode_url, './data/postcode.csv.zip')
    extract_file('./data/postcode.csv.zip', './data/postcode.csv')

def load_london_wards(url):
    request_url(url, './data/london-wards.zip')
    extract_file('./data/london-wards.zip', './data/')

def region_data(conn, start_date, end_date, region_type, region_name):
    return sql.join_by_region(conn, start_date, end_date, region_type, region_name)

def map_data(file):
    return gpd.read_file(file)

def main():
    database_details = {"url": "assessment-mariadb.c0qk4q5ftzh1.eu-west-2.rds.amazonaws.com", 
                    "port": 3306}
    
    username, password = read_credentials()
    url = database_details['url']

    conn = sql.create_connection(username, password, url, None)
    sql.create_database(conn)

    conn = sql.create_connection(username, password, url, 'property_prices')
    create_pp_data(conn)
    create_postcode_data(conn)
    load_gov_data(conn, "http://prod2.publicdata.landregistry.gov.uk.s3-website-eu-west-1.amazonaws.com/")
    load_postcode_data(conn, "https://www.getthedata.com/downloads/open_postcode_geo.csv.zip")
    load_london_wards("https://data.london.gov.uk/download/statistical-gis-boundary-files-london/9ba8c833-6370-4b11-abdc-314aa020d5e0/statistical-gis-boundaries-london.zip")

main()