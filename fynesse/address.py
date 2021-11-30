# This file contains code for suporting addressing questions in the data
import numpy as np
import pandas as pd
import datetime 

from sklearn.model_selection import train_test_split
import statsmodels.api as sm
import statsmodels.formula.api as smf

from fynesse import assess, access

def pick_features(data, columns=['longitude', 'latitude']):
  print(f'Picking features: {columns}...')
  
  features = data[columns]
  assert not features.isnull().values.any()

  return np.array(features.values, dtype=float)

def pick_response(data, column='price'):
  return np.array(data[column].values, dtype=float)

def train_validation_split(data, tags=['longitude', 'latitude'], test_size=0.2):
  print(f'Spliting data into training and validation with test size: {test_size}...')
  x_train, x_test, y_train, y_test = train_test_split(pick_features(data, tags), pick_response(data), test_size=test_size, random_state=0)
  return x_train, x_test, y_train, y_test

def get_date_range(date, days=365):
    date_obj = datetime.date.fromisoformat(date)
    end_date = (date_obj - datetime.timedelta(1)).isoformat()
    start_date = (date_obj - datetime.timedelta(days)).isoformat()
    return (start_date, end_date)

def predict_price(conn, latitude, longitude, date, property_type):
    start_date, end_date = get_date_range(date)
    south, north = latitude - 0.05, latitude + 0.05
    west, east = longitude - 0.04, longitude + 0.04

    pois_tags = {'amenity': True,
            'historic': True,
            'leisure': True,
            'shop': True, 
            'tourism': True
    }

    feature_tags = ['latitude', 'longitude'] + list(pois_tags.keys())
    
    print(f'Getting house data...')
    raw = access.box_data(conn, (north, south, west, east), start_date, end_date, property_type)
    data = assess.assess_houses(raw)

    if len(data) < 40:
        print(f'WARNING: FEW DATA POINTS. Trying to create model from {len(data)} data points...')

    # reduce data size because of openstreetmap
    sample = data.sample(min(40, len(data)))
    sample = sample.reset_index()

    print(f'Getting OpenStreetMap features...')
    raw_pois = access.pois_data(sample, pois_tags)
    pois_df = assess.assess_pois(raw_pois, pois_tags)

    total_data = pd.concat([sample, pois_df], axis=1)

    print(f'Building a model for the region around the house...')
    x_train, x_test, y_train, y_test = train_validation_split(total_data, feature_tags, 0.2)
    model = sm.GLM(y_train, x_train, family=sm.families.Poisson()).fit()

    print(f'Validate the model...')
    predict = model.get_prediction(x_test).summary_frame(alpha=0.5)
    y_pred = predict['mean']
    print(f'Average difference: {(np.abs(y_pred - y_test)).mean()}')
    print(f'Maximum difference: {(np.abs(y_pred - y_test)).max()}')
    print(f'Minimum difference: {(np.abs(y_pred - y_test)).min()}')

    print(f'Predicting price for house...')
    x_df = pd.DataFrame({'longitude': [longitude], 'latitude': [latitude]})
    x_pois = assess.assess_pois(access.pois_data(x_df, pois_tags), pois_tags)
    
    X = pd.concat([x_df, x_pois], axis=1)
    prediction = model.get_prediction(pick_features(X, columns=feature_tags)).summary_frame(alpha=0.5)
    return prediction, model
