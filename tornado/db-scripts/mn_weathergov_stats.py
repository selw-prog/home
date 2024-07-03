import mysql.connector
from dotenv import dotenv_values
import pandas as pd
import geopandas as gpd

# schema 
# county(countyID INT, county VARCHAR, state VARCHAR, geometry TEXT) - PK countyID
# tornado (countyID INT, year INT, numTornados INT) - PK (countyID, year) - FK countyID references county(countyID)


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