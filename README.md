# UK Housing Prices Predictor
This project is part of the Advanced Data Science Course for Part II of the Computer Science Tripos at the University of Cambridge. This predictor builds a Generalized Linear Model on the fly using coordinate data as well as points of interest around these coordinates from OpenStreetMap to fit the parameters. 

The project structure follows the fynesse template, as seen in the tree below. 
```
fynesse            
├─ access_scripts  
│  ├─ __init__.py  
│  ├─ opm.py       
│  ├─ schemas.py   
│  └─ sql.py      
|
├─ __init__.py     
├─ access.py       
├─ address.py      
├─ assess.py
|
├─ config.py       
└─ defaults.yml    
```

## Access

The `access` module is composed of a main file, called `access.py`, and an additional folder `access_scripts` that contains code for SQL queries to MariaDB and OpenStreetMap queries. In addition, `schemas.py` contains various constants used in these queries, such as column names for SQL tables and table creation code.

Functions in `access_scripts` can be accessed on their own by importing the right module:
```
from fynesse.access_scripts import sql, opm, schemas
```
However, `access.py` contains functions that have been used for downloading and uploading data (from various URLs to MariaDB, using PyMySql) that the reader might find easier to use as they abstract away some constants:
1. `load_gov_data(connection, gov_url)` loads all UK Price Paid data, from 2021 to 1995. It downloads each `csv` file and uploads it to MariaDB. 
2. `load_postcode_data(connection, postcode_url)` loads all postcode data in the UK. It does this in a similar manner with the function above.
3. `table_head(connection, table_name, limit=5)` loads the head of an SQL table. This is useful for checking that a table has been loaded successfully.

Among the other functions that the reader will find in this file, three are of special interest:
1. `region_data` returns a pandas dataframe with all the house data (including coordinates) from a particular region. For example:```cambridge = access.region_data(connecion, '2021-01-01', '2021-12-31', 'town_city', 'Cambridge')``` will return all houses that have been sold in Cambridge over the past year.
2. `box_data` returns returns all of the houses of a particular property type with coordinates a bounding box. 
3. `pois_data` returns all POIs (points of interest) with the given tags for a bouding box from OpenStreetMap.

## Assess

Understanding what is in the data. Is it what it's purported to be, how are missing values encoded, what are the outliers, what does each variable represent and how is it encoded.

Data that is accessible can be imported (via APIs or database calls or reading a CSV) into the machine and work can be done understanding the nature of the data. The important thing to say about the assess aspect is that it only includes things you can do *without* the question in mind. This runs counter to many ideas about how we do data analytics. The history of statistics was that we think of the question *before* we collect data. But that was because data was expensive, and it needed to be excplicitly collected. The same mantra is true today of *surveillance data*. But the new challenge is around *happenstance data*, data that is cheaply available but may be of poor quality. The nature of the data needs to be understood before its integrated into analysis. Unfortunately, because the work is conflated with other aspects, decisions are sometimes made during assessment (for example approaches to imputing missing values) which may be useful in one context, but are useless in others. So the aim in *assess* is to only do work that is repeatable, and make that work available to others who may also want to use the data.

## Address

The final aspect of the process is to *address* the question. We'll spend the least time on this aspect here, because it's the one that is most widely formally taught and the one that most researchers are familiar with. In statistics, this might involve some confirmatory data analysis. In machine learning it may involve designing a predictive model. In many domains it will involve figuring out how best to visualise the data to present it to those who need to make the decisions. That could involve a dashboard, a plot or even summarisation in an Excel spreadsheet.
