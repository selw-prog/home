import mysql.connector
import logging
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt

from pathlib import Path
from datetime import datetime
from dotenv import dotenv_values
from shapely import wkt

sqlserver_config = dotenv_values('../../.env')
cnx = mysql.connector.connect(user = sqlserver_config['USERNAME'], password = sqlserver_config['PASSWORD'],
                              host = sqlserver_config['IPADDRESS'], database = sqlserver_config['DATABASE'])
cursor = cnx.cursor()
log_filename = datetime.now().strftime('%Y_%m_%H_%M_misc-queries.log')
log_path = Path(r'C:\Users\seanr\OneDrive\Documents\Logs\Python')
logging.basicConfig(filename='{p}\{f}'.format(p = log_path, f = log_filename), encoding='utf-8', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

def get_all_county_info() -> pd.DataFrame:
    query = ("SELECT * FROM county")
    cursor.execute(query)
    df = pd.DataFrame(cursor, columns = cursor.column_names)
    return df

def test_wkt_convert(state:str) -> pd.DataFrame:
    query = ("SELECT * FROM county WHERE state = '{s}'".format(s = state))
    cursor.execute(query)
    df = pd.DataFrame(cursor, columns = cursor.column_names)
    df['geometry'] = gpd.GeoSeries.from_wkt(df['geometry'])
    gdf = gpd.GeoDataFrame(df, geometry = 'geometry')
    gdf.plot()
    
def test_join(): 
    query = ("SELECT county.county,county.state,tornado.year,tornado.numTornados FROM county INNER JOIN tornado ON county.countyID=tornado.countyID WHERE county.state = 'Minnesota'") # returns 87 * 12 = 1044 rows, will not scale well
    cursor.execute(query)
    df = pd.DataFrame(cursor, columns = cursor.column_names)
    return df
    #df['geometry'] = gpd.GeoSeries.from_wkt(df['geometry'])
    #gdf = gpd.GeoDataFrame(df, geometry = 'geometry')
    #return gdf
    

# TESTS BELOW

county_data = get_all_county_info()
#query = ("DELETE FROM tornado WHERE countyId={id}")
#for row in wi_tornado_county_tables_merged['countyId'].drop_duplicates():
#    logging.info('Deleting countyId {id} from tornado_stats table.'.format(id = row))
#    cursor.execute(query.format(id = row))
#query = ("SELECT * FROM tornado")
#cursor.execute(query)
#df = pd.DataFrame(cursor, columns = cursor.column_names)