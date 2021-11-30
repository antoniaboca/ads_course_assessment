import pandas as pd
import pymysql
import datetime

from fynesse.access_scripts.schemas import JOIN_COLUMNS, PRICE_PROP_COLUMNS, PRICE_PROP_SQL_COLUMNS


regions = ['locality', 'town_city', 'district', 'county', 'country']

def execute_query(conn, query):
        cur = conn.cursor()
        aff = cur.execute(query)
        print(f'Affected rows: {aff}')
        rows = cur.fetchall()
        cur.close()
        conn.commit()
        return rows
    
def primary_key_query(table, name):
        return """
        ALTER TABLE `{0}`
            ADD PRIMARY KEY (`{1}`);

        ALTER TABLE `{0}`
            MODIFY `{1}` bigint(20) unsigned NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=1;
        """.format(table, name)

def database_size(conn):
        query = """
        SELECT TABLE_SCHEMA, TABLE_NAME,
        round(((DATA_LENGTH + INDEX_LENGTH) / 1024 / 1024), 2) As "Approximate size (MB)"
        FROM information_schema.TABLES
        WHERE TABLE_SCHEMA NOT IN ('mysql', 'information_schema', 'performance_schema');
        """

        rows = execute_query(conn, query)
        return pd.DataFrame(rows, columns=['TABLE_SCHEMA', 'TABLE_NAME', 'Approximate size (MB)'])

def load_csv(conn, file, table):
    query = """
                    LOAD DATA LOCAL INFILE '{}' INTO TABLE {}
                    FIELDS TERMINATED BY ',' 
                    OPTIONALLY ENCLOSED BY '"'
                    LINES STARTING BY '' TERMINATED BY '\n'
                    IGNORE 1 LINES;
                    """.format(file, table)
    rows = execute_query(conn, query)
    return rows

def load_from_head(conn, table, limit=5):
    query = """
        SELECT * from {} LIMIT {}
        """.format(table, limit)
    rows = execute_query(conn, query)
    return rows

def delete_table(conn, table):
        query = "DELETE FROM {}".format(table)
        return execute_query(conn, query)

    
def get_count(conn, table):
        query = """SELECT COUNT(*) FROM property_prices.{}""".format(table)
        rows = execute_query(conn, query)
        return rows

def join_by_region(conn, start_date, end_date, region_type=None, region_name=None):
        format = "%Y-%m-%d"
        try:
            datetime.datetime.strptime(start_date, format) and datetime.datetime.strptime(end_date, format)
        except ValueError:
            raise Exception("Please insert a correct date string format: [YYYY-mm-dd]")
        if region_type is None or region_type not in regions:
            raise Exception("Please select region type: [locality], [town_city], [district], [county], [country]")
    
        region_name = region_name.upper()
        cur = conn.cursor()
        query = """
        SELECT p.price, p.date_of_transfer, p.property_type, p.new_build_flag, c.postcode_area, c.postcode_district, p.postcode, c.latitude, c.longitude, p.locality, p.town_city, p.district, p.county, c.country FROM
            (SELECT * FROM property_prices.postcode_data) c
        INNER JOIN
            (SELECT * FROM pp_data WHERE {} = "{}" AND date_of_transfer between '{}' and '{}') p
        ON 
            p.postcode = c.postcode
        """.format(region_type, region_name, start_date, end_date)

        aff = cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        print('Affected rows: {}'.format(aff))
        return pd.DataFrame(rows, columns=JOIN_COLUMNS)


def join_bounding_box(conn, box, start_time, end_time, property_type):
  format = "%Y-%m-%d"
  north, south, west, east = box
  try:
    datetime.datetime.strptime(start_time, format) and datetime.datetime.strptime(end_time, format)
  except ValueError:
    raise Exception("Please insert a correct date string format: [YYYY-mm-dd]")
  
  if property_type not in ['O', 'S', 'D', 'T', 'F']:
    raise Exception("Please choose property_type from ['O', 'S', 'D', 'T', 'F']")

  query = f"""
    SELECT p.price, p.date_of_transfer, p.postcode, p.property_type, p.new_build_flag, p.tenure_type, p.locality, p.town_city, p.district, p.county, c.country, c.latitude, c.longitude FROM
      (SELECT postcode, country, latitude, longitude FROM postcode_data
      WHERE latitude BETWEEN '{south}' AND '{north}' AND longitude BETWEEN '{west}' AND '{east}') c
    INNER JOIN  
      (SELECT * FROM pp_data
        WHERE date_of_transfer BETWEEN '{start_time}' AND '{end_time}' AND property_type = '{property_type}'
        AND postcode NOT IN (SELECT postcode FROM prices_coordinates_data)) p
    ON
      p.postcode = c.postcode 
  """

  rows = execute_query(conn, query)
  return pd.DataFrame(rows, columns=PRICE_PROP_COLUMNS)

def update_prices_coordinates_data(conn, df):
  df.to_csv('temp_join.csv', index=False)
  load_csv(conn, 'temp_join.csv', 'prices_coordinates_data')
  print(f'Loaded rows from temp_join.csv to prices_coordinates_data')

def bounding_box_data(conn, box, start_date, end_date, property_type):
  format = "%Y-%m-%d"
  north, south, west, east = box
  try:
    datetime.datetime.strptime(start_date, format) and datetime.datetime.strptime(end_date, format)
  except ValueError:
    raise Exception("Please insert a correct date string format: [YYYY-mm-dd]")
  
  if property_type not in ['O', 'S', 'D', 'T', 'F']:
    raise Exception("Please choose property_type from ['O', 'S', 'D', 'T', 'F']")

  query = f"""
    SELECT * FROM prices_coordinates_data 
      WHERE lattitude BETWEEN '{south}' AND '{north}' AND longitude BETWEEN '{west}' AND '{east}'
      AND date_of_transfer BETWEEN '{start_date}' AND '{end_date}'
      AND property_type = '{property_type}'
  """

  rows = execute_query(conn, query)
  return pd.DataFrame(rows, columns=PRICE_PROP_SQL_COLUMNS)