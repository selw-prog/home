import mysql.connector
import requests
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import dotenv_values
from shapely import wkt
from lxml import etree

# schema 
# county(countyID INT, county VARCHAR, state VARCHAR, geometry TEXT) - PK countyID
# tornado (countyID INT, year INT, numTornados INT) - PK (countyID, year) - FK countyID references county(countyID)

YEARS = ['2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021'] # weather.gov site does not have data past 2010 available
sqlserver_config = dotenv_values('.env')
cnx = mysql.connector.connect(user = sqlserver_config['USERNAME'], password = sqlserver_config['PASSWORD'],
                              host = sqlserver_config['IPADDRESS'], database = sqlserver_config['DATABASE'])
cursor = cnx.cursor()

def add_minnesota_counties_to_db():
    add_mn_county = ("INSERT INTO county "
              "(countyID, county, state, geometry) "
              "VALUES (default,%(county)s, %(state)s, %(geometry)s)")
    gdf = gpd.read_file('../cb_2023_us_county_500k') # get geodataframe, source https://www2.census.gov/geo/tiger/GENZ2023/gdb/
    gdf = gdf[gdf.STATE_NAME == 'Minnesota']
    gdf = gdf.to_wkt() # convert all geometry columns to well known text for storage in db
    for_county_table = gdf[['NAME','STATE_NAME','geometry']]
    for index,row in for_county_table.iterrows():
        db_insert_data = {
            'county' : row['NAME'],
            'state' : row['STATE_NAME'],
            'geometry' : row['geometry']
        }
        cursor.execute(add_mn_county, db_insert_data)
        cnx.commit()
    cursor.close()
    cnx.close()

def add_tornado_stats_to_db():
    add_tornado_stats = ("INSERT INTO tornado "
                  "(countyID, year, numTornados) "
                  "VALUES (%(countyID)s, %(year)s, %(numTornados)s)")
    tornado_data = {}
    for year in YEARS: 
        url = 'https://www.weather.gov/source/mpx/TornadoStats/minnesotaTornadoes{y}.xml'.format(y = year)
        raw = requests.get(url)
        root = etree.fromstring(raw.content)
        data = []
        for child in root.iterchildren():
            data.append(dict(child.attrib))
        counties = {}
        for event in data: # calculating statistics for each county 
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
    tornado_df = pd.DataFrame.from_dict(tornado_data)
    query = ("SELECT * FROM county")
    cursor.execute(query)
    df = pd.DataFrame(cursor, columns = cursor.column_names)
    df = df.merge(tornado_df, how='left', left_on='county', right_index = True) # merging gdf with tornado statistics
    for year in YEARS: # set all NaN values to 0 for plotting
        df.loc[df[year].isnull(),year] = 0
    for year in YEARS:
        for index,row in df.iterrows():
            db_insert_data = {
                'countyID' : row['countyID'],
                'year' : year,
                'numTornados' : row[year]
            }
            cursor.execute(add_tornado_stats, db_insert_data)
            cnx.commit()
    return df

def test_query() -> pd.DataFrame:
    query = ("SELECT * FROM county")
    cursor.execute(query)
    df = pd.DataFrame(cursor, columns = cursor.column_names)
    return df

def test_wkt_convert() -> pd.DataFrame:
    query = ("SELECT * FROM county")
    cursor.execute(query)
    df = pd.DataFrame(cursor, columns = cursor.column_names)
    df['geometry'] = gpd.GeoSeries.from_wkt(df['geometry'])
    gdf = gpd.GeoDataFrame(df, geometry = 'geometry')
    gdf.plot()
    
def test_join(): 
    query = ("SELECT county.countyId,county.county,county.state,county.geometry,tornado.year,tornado.numTornados FROM county INNER JOIN tornado ON county.countyID=tornado.countyID") # returns 87 * 12 = 1044 rows, will not scale well
    cursor.execute(query)
    df = pd.DataFrame(cursor, columns = cursor.column_names)
    df['geometry'] = gpd.GeoSeries.from_wkt(df['geometry'])
    gdf = gpd.GeoDataFrame(df, geometry = 'geometry')
    return gdf

#data = test_query()
#test_wkt_convert()
#df = add_tornado_stats_to_db()
join = test_join()