import mysql.connector
import requests
import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import csv
from pathlib import Path
from dotenv import dotenv_values
from shapely import wkt
from lxml import etree

# schema 
# county(countyID INT, county VARCHAR, state VARCHAR, geometry TEXT) - PK countyID
# tornado (countyID INT, year INT, numTornados INT) - PK (countyID, year) - FK countyID references county(countyID)

YEARS = ['2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021'] # weather.gov site does not have data past 2010 available
sqlserver_config = dotenv_values('../../.env')
cnx = mysql.connector.connect(user = sqlserver_config['USERNAME'], password = sqlserver_config['PASSWORD'],
                              host = sqlserver_config['IPADDRESS'], database = sqlserver_config['DATABASE'])
cursor = cnx.cursor()

def add_counties_to_db(state:str):
    add_county = ("INSERT INTO county "
              "(countyID, county, state, geometry) "
              "VALUES (default,%(county)s, %(state)s, %(geometry)s)")
    gdf = gpd.read_file('../cb_2023_us_county_500k') # get geodataframe, source https://www2.census.gov/geo/tiger/GENZ2023/gdb/
    gdf = gdf[gdf.STATE_NAME == '{s}'.format(s = state)]
    gdf = gdf.to_wkt() # convert all geometry columns to well known text for storage in db
    for_county_table = gdf[['NAME','STATE_NAME','geometry']]
    for index,row in for_county_table.iterrows():
        db_insert_data = {
            'county' : row['NAME'],
            'state' : row['STATE_NAME'],
            'geometry' : row['geometry']
        }
        cursor.execute(add_county, db_insert_data)
        cnx.commit()
    cursor.close()
    cnx.close()

def add_mn_tornado_stats_to_db():
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

def test():
    add_tornado_stats = ("INSERT INTO Minnesota "
                  "(id, county_name, county_state, num_tornados_2010, num_tornados_2011, num_tornados_2012, num_tornados_2013, num_tornados_2014, num_tornados_2015, num_tornados_2016, num_tornados_2017, num_tornados_2018, num_tornados_2019, num_tornados_2020, num_tornados_2021) "
                  "VALUES (default, %(county_name)s, %(county_state)s, %(num_tornados_2010)s, %(num_tornados_2011)s, %(num_tornados_2012)s, %(num_tornados_2013)s, %(num_tornados_2014)s, %(num_tornados_2015)s, %(num_tornados_2016)s, %(num_tornados_2017)s, %(num_tornados_2018)s, %(num_tornados_2019)s, %(num_tornados_2020)s, %(num_tornados_2021)s)")
    data = []
    with open('C:\\Users\\seanr\\OneDrive\\Documents\\Home-Lab\\10-31-24_tornado-stats.csv') as csvfile:
        reader = csv.DictReader(csvfile)
        county_data = {}
        county_data['name'] = 'Clay'
        county_data['state'] = 'Minnesota'
        for row in reader:
            if county_data['name'] != row['county']:
                print(county_data)
                data.append(county_data)
                county_data = {}
                county_data['name'] = row['county']
                county_data['state'] = row['state']
                county_data['num_tornados_{y}'.format(y = row['year'])] = row['numTornados']
            else: 
                county_data['num_tornados_{y}'.format(y = row['year'])] = row['numTornados']
    #for county in data:
    #    db_insert_data = {
    #        'county_name' : county['name'],
    #        'county_state' : county['state'],
    #        'num_tornados_2010' : county['num_tornados_2010'],
    #        'num_tornados_2011' : county['num_tornados_2011'],
    #        'num_tornados_2012' : county['num_tornados_2012'],
    #        'num_tornados_2013' : county['num_tornados_2013'],
    #        'num_tornados_2014' : county['num_tornados_2014'],
    #        'num_tornados_2015' : county['num_tornados_2015'],
    #        'num_tornados_2016' : county['num_tornados_2016'],
    #        'num_tornados_2017' : county['num_tornados_2017'],
    #        'num_tornados_2018' : county['num_tornados_2018'],
    #        'num_tornados_2019' : county['num_tornados_2019'],
    #        'num_tornados_2020' : county['num_tornados_2020'],
    #        'num_tornados_2021' : county['num_tornados_2021']
    #    }
    #    cursor.execute(add_tornado_stats, db_insert_data)
    #    print('inserted data {db}'.format(db = db_insert_data))
    #    cnx.commit()
    return data

d = test()
#add_mn_tornado_stats_to_new_table()