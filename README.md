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

The `assess` module contains functions that check the validity of the values in the data and plot various graphs that help with exploratory data analysis. Among the functions, three have been the most useful in this project:
1. `assess_houses` checks that some columns are that are necessary for data analysis do not contain `NaN` values 
2. `assess_pois` checks that whether POIs exist for all given tags and computes the total number of POIs per house
3. `draw_correlation` fits a line to a dataset and prints both a plot and the pearson correlation of the `xs` and `ys`.

The assess module was used to "see" how the data looks like; what are the differences between types of properties, what POIs influence house prices most. This modules has helped make decision about the parameters of the model - for example, in this module I have decided to use the Poisson family for my GLM. 
## Address
The address module contains a main function:
```
prediction, model = predict_price(conn, latitude, longitude, date, property_type)
```

This function builds a model on the fly, using all houses of the same `property_type` surrounding `(latitude, longitude)`. The steps it takes are the following:
1. It joins housing data and postcode data to find the coordinates of all houses in a given bouding box
2. It extracts all POIs of interest for each house 
3. It encodes the coordinate information and the POIs into a matrix of features 
4. It splits the dataset into the training set and the validation set
5. It trains the model 
6. It validates the model, by plotting the difference between the predicted prices and the actual prices
7. It return the model and a prediction 

All other functions in this module are functions that implement the steps above. 
