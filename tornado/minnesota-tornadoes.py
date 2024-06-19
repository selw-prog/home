import requests
import pandas as pd
import geopandas as gpd
import os
from lxml import etree

def get_tornado_data(year:int) -> dict:
    tornado_data = {}
    url = 'https://www.weather.gov/source/mpx/TornadoStats/minnesotaTornadoes{y}.xml'.format(y = year) # seems like they don't have data avail past 2010
    raw = requests.get(url)
    root = etree.fromstring(raw.content)
    data = []
    for child in root.iterchildren():
        data.append(dict(child.attrib))
    counties = {}
    for event in data:
        if ',' in event['counties']:
            for c in event['counties'].split(','):
                county = c.strip()
                if county in counties.keys():
                    counties[county] += 1
                else:
                    counties[county] = 1
        else:
            county = event['counties'].strip()
        if county in counties.keys():
            counties[county] += 1
        else:
            counties[county] = 1
    tornado_data[year] = counties
    return tornado_data

def generate_map(year:int):
    gdf = gpd.read_file(os.getcwd()+'/cb_2023_us_county_500k') # get geodataframe, source https://www2.census.gov/geo/tiger/GENZ2023/gdb/
    gdf = gdf[gdf.STATE_NAME == 'Minnesota']
    tornado_df = pd.DataFrame.from_dict(get_tornado_data(year))
    gdf = gdf.merge(tornado_df, how='left', left_on='NAME', right_index = True)
    gdf.loc[gdf[year].isnull(),year] = 0 # set all NaN values to 0 for plotting
    gdf.plot(column=year,cmap='OrRd',edgecolor='black',legend=True)


generate_map(2020)