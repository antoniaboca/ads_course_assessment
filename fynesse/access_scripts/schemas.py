DATABASE_CREATE = """
    SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';
    SET time_zone = '+00:00';

    CREATE DATABASE IF NOT EXISTS property_prices DEFAULT CHARACTER SET utf8 COLLATE utf8_bin;
"""

PP_DATA_SCHEMA = """
DROP TABLE IF EXISTS property_prices.pp_data;

CREATE TABLE IF NOT EXISTS pp_data (
  transaction_unique_identifier tinytext COLLATE utf8_bin NOT NULL,
  price int(10) unsigned NOT NULL,
  date_of_transfer date NOT NULL,
  postcode varchar(8) COLLATE utf8_bin,
  property_type varchar(1) COLLATE utf8_bin NOT NULL,
  new_build_flag varchar(1) COLLATE utf8_bin NOT NULL,
  tenure_type varchar(1) COLLATE utf8_bin NOT NULL,
  primary_addressable_object_name tinytext COLLATE utf8_bin NOT NULL,
  secondary_addressable_object_name tinytext COLLATE utf8_bin,
  street tinytext COLLATE utf8_bin,
  locality tinytext COLLATE utf8_bin,
  town_city tinytext COLLATE utf8_bin NOT NULL,
  district tinytext COLLATE utf8_bin NOT NULL,
  county tinytext COLLATE utf8_bin NOT NULL,
  ppd_category_type varchar(2) COLLATE utf8_bin NOT NULL,
  record_status varchar(2) COLLATE utf8_bin NOT NULL,
  db_id bigint(20) unsigned NOT NULL
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;

ALTER TABLE pp_data
ADD PRIMARY KEY (db_id);

ALTER TABLE pp_data
MODIFY db_id bigint(20) unsigned NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=1;

CREATE OR REPLACE INDEX postcode USING HASH
  ON pp_data
    (postcode);

CREATE OR REPLACE INDEX date USING HASH
  ON pp_data 
    (date_of_transfer);
"""

POSTCODE_DATA_SCHEMA = """
DROP TABLE IF EXISTS postcode_data;
CREATE TABLE IF NOT EXISTS postcode_data (
  postcode varchar(8) COLLATE utf8_bin NOT NULL,
  status enum('live','terminated') NOT NULL,
  usertype enum('small', 'large') NOT NULL,
  easting int unsigned,
  northing int unsigned,
  positional_quality_indicator int NOT NULL,
  country enum('England', 'Wales', 'Scotland', 'Northern Ireland', 'Channel Islands', 'Isle of Man') NOT NULL,
  latitude decimal(11,8) NOT NULL,
  longitude decimal(10,8) NOT NULL,
  postcode_no_space tinytext COLLATE utf8_bin NOT NULL,
  postcode_fixed_width_seven varchar(7) COLLATE utf8_bin NOT NULL,
  postcode_fixed_width_eight varchar(8) COLLATE utf8_bin NOT NULL,
  postcode_area varchar(2) COLLATE utf8_bin NOT NULL,
  postcode_district varchar(4) COLLATE utf8_bin NOT NULL,
  postcode_sector varchar(6) COLLATE utf8_bin NOT NULL,
  outcode varchar(4) COLLATE utf8_bin NOT NULL,
  incode varchar(3)  COLLATE utf8_bin NOT NULL,
  db_id bigint(20) unsigned NOT NULL
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin;

ALTER TABLE postcode_data
 ADD PRIMARY KEY (db_id);

ALTER TABLE postcode_data
 MODIFY db_id bigint(20) unsigned NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=1;


CREATE INDEX postcode USING HASH
  ON postcode_data
    (postcode);
"""

PRICES_COORDINATES_DATA_SCHEMA = """
DROP TABLE IF EXISTS property_prices.prices_coordinates_data;
CREATE TABLE IF NOT EXISTS prices_coordinates_data (
  price  int(10) unsigned NOT NULL,
  date_of_transfer  date NOT NULL,
  postcode  varchar(8) COLLATE utf8_bin NOT NULL,
  property_type  varchar(1) COLLATE utf8_bin NOT NULL,
  new_build_flag  varchar(1) COLLATE utf8_bin NOT NULL,
  tenure_type  varchar(1) COLLATE utf8_bin NOT NULL,
  locality  tinytext COLLATE utf8_bin NOT NULL,
  town_city  tinytext COLLATE utf8_bin NOT NULL,
  district  tinytext COLLATE utf8_bin NOT NULL,
  county  tinytext COLLATE utf8_bin NOT NULL,
  country  enum('England', 'Wales', 'Scotland', 'Northern Ireland', 'Channel Islands', 'Isle of Man') NOT NULL,
  lattitude decimal(11,8) NOT NULL,
  longitude decimal(10,8) NOT NULL,
  db_id bigint(20) unsigned NOT NULL
) DEFAULT CHARSET=utf8 COLLATE=utf8_bin AUTO_INCREMENT=1 ;

ALTER TABLE prices_coordinates_data
 ADD PRIMARY KEY (db_id);

ALTER TABLE prices_coordinates_data
  MODIFY db_id bigint(20) unsigned NOT NULL AUTO_INCREMENT,AUTO_INCREMENT=1;

CREATE INDEX date USING HASH
  ON prices_coordinates_data 
    (date_of_transfer);
"""

GOV_COLUMNS = ['transaction_unique_identifier', 
           'price', 
           'date_of_transfer', 
           'postcode', 
           'property_type', 
           'new_build_flag', 
           'tenure_type', 
           'primary_addressable_object_name',
           'secondary_addressable_object_name',
           'street',
           'locality',
           'town_city',
           'district',
           'county',
           'ppd_category_type',
           'record_status']

PP_COLUMNS = ['transaction_unique_identifier', 
           'price', 
           'date_of_transfer', 
           'postcode', 
           'property_type', 
           'new_build_flag', 
           'tenure_type', 
           'primary_addressable_object_name',
           'secondary_addressable_object_name',
           'street',
           'locality',
           'town_city',
           'district',
           'county',
           'ppd_category_type',
           'record_status',
           'db_id']

PRICE_PROP_COLUMNS = ['price', 'date_of_transfer', 'postcode', 'property_type', 
                      'new_build_flag', 'tenure_type', 'locality', 'town_city', 'district',
                      'county', 'country', 'latitude', 'longitude']

PRICE_PROP_SQL_COLUMNS = ['price', 'date_of_transfer', 'postcode', 'property_type', 
                      'new_build_flag', 'tenure_type', 'locality', 'town_city', 'district',
                      'county', 'country', 'latitude', 'longitude', 'db_id']

POSTCODE_COLUMNS = ['postcode',
               'status',
               'usertype',
               'easting',
               'northing',
               'positional_quality_indicator',
               'country',
               'latitude',
               'longitude',
               'postcode_no_space',
               'postcode_fixed_width_seven',
               'postcode_fixed_width_eight',
               'postcode_area',
               'postcode_district',
               'postcode_sector',
               'outcode',
               'incode']

POSTCODE_SQL_COLUMNS = ['postcode',
               'status',
               'usertype',
               'easting',
               'northing',
               'positional_quality_indicator',
               'country',
               'latitude',
               'longitude',
               'postcode_no_space',
               'postcode_fixed_width_seven',
               'postcode_fixed_width_eight',
               'postcode_area',
               'postcode_district',
               'postcode_sector',
               'outcode',
               'incode',
               'db_id']

JOIN_COLUMNS = [
    'price', 
    'date_of_transfer',
    'property_type', 
    'new_build_flag', 
    'postcode_area', 
    'postcode_district', 
    'postcode', 
    'latitude', 
    'longitude', 
    'locality', 
    'town_city',
    'district', 
    'county', 
    'country']