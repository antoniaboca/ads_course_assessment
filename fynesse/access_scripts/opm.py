import osmnx as ox
import pandas as pd

def get_pois_for_house(long, lat, tags, len=0.005):
        box_width = len
        box_height = len
        longitude = float(long)
        latitude = float(lat)
        north = latitude + box_height/2.0
        south = latitude - box_width/2.0
        west = longitude - box_width/2.0
        east = longitude + box_width/2.0

        pois = ox.geometries_from_bbox(north, south, east, west, tags)
        return pois

def get_pois_stats(longs, lats, tags, len=0.005):
    per_house = []
    for long, lat in zip(longs, lats):
        pois = get_pois_for_house(long, lat, tags, len)
        filtered = {}
        for tag in tags:
            if tag in pois.columns:
                n_pois = pois[pois[tag].notnull()]
                if not n_pois.empty:
                    filtered[tag] = len(n_pois)
                else:
                    filtered[tag] = 0
            else:
                filtered[tag] = 0
        per_house.append(filtered)

    return pd.DataFrame(per_house)
