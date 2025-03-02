import cv2
import pytesseract
import mysql.connector
import logging
import os
import json
import pandas as pd
import re
import csv

from pathlib import Path
from datetime import datetime
from dotenv import dotenv_values
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
log_filename = datetime.now().strftime('%Y_%m_%H_%M_wi_data_insert.log')
log_path = Path(r'C:\Users\seanr\OneDrive\Documents\Logs\Python')
logging.basicConfig(filename='{p}\{f}'.format(p = log_path, f = log_filename), encoding='utf-8', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

sqlserver_config = dotenv_values('../../.env')
cnx = mysql.connector.connect(user = sqlserver_config['USERNAME'], password = sqlserver_config['PASSWORD'],
                              host = sqlserver_config['IPADDRESS'], database = sqlserver_config['DATABASE'])
cursor = cnx.cursor()

def add_wi_tornado_stats_to_db(tornado_df, year):
    add_tornado_stats = ("INSERT INTO tornado "
                  "(countyID, year, numTornados) "
                  "VALUES (%(countyID)s, %(year)s, %(numTornados)s)")
    query = ("SELECT * FROM county WHERE state = 'Wisconsin'")
    cursor.execute(query)
    df = pd.DataFrame(cursor, columns = cursor.column_names)
    df = df.merge(tornado_df, how='left', left_on='county', right_index = True) # merging gdf with tornado statistics
    df = df.fillna(0)
    for index,row in df.iterrows():
        db_insert_data = {
            'countyID' : row['countyID'],
            'year' : year,
            'numTornados' : row['numTornados']
        }
        logging.info(db_insert_data)
        cursor.execute(add_tornado_stats, db_insert_data)
        cnx.commit()
    logging.info('All data for year {y} added to database.'.format(y = year))
    return df

def update_wi_tornado_stats(tornado_df): # for updating stats in db
    update_tornado_stats = ("UPDATE tornado "
                            "SET numTornados = {num}"
                            "WHERE countyID = {id}")
    select_current_tornado_stats = ("SELECT * FROM tornado "
                                    "WHERE countyID = {id}")
    query = ("SELECT * FROM county WHERE state = 'Wisconsin'")
    logging.info('Executed {q} against {db}.'.format(q = query, db = sqlserver_config['IPADDRESS']))
    cursor.execute(query)
    df = pd.DataFrame(cursor, columns = cursor.column_names)
    df = df.merge(tornado_df, how='left', left_on='county', right_index = True) # merging gdf with tornado statistics
    df = df.fillna(0)
    logging.info('Looping through merged dataframe to update statistics.')
    for index,row in df.iterrows():
        logging.info('Updating county ID {c}.'.format(c = row['countyID']))
        logging.info('Executed {q} against {db}.'.format(q = select_current_tornado_stats, db = sqlserver_config['IPADDRESS']))
        cursor.execute(select_current_tornado_stats.format(id = row['countyID']))
        current_data = pd.DataFrame(cursor, columns = cursor.column_names) # get current data
        updated_tornado_count = current_data['numTornados'].values[0] + row['numTornados']
        logging.info('Current tornado count for county ID {id} is {num}. New value should be {new}.'.format(id = current_data['countyID'].values[0], num = current_data['numTornados'].values[0], new = updated_tornado_count))
        logging.info('Updating database..')
        cursor.execute(update_tornado_stats.format(num = updated_tornado_count, id = row['countyID']))
        cnx.commit()




def insert_json_file(file_path):
    add_tornado_stats = ("INSERT INTO wisconsin "
                  "(id, county_name, county_state, num_tornados_2014, num_tornados_2015, num_tornados_2016, num_tornados_2017, num_tornados_2018, num_tornados_2019, num_tornados_2020, num_tornados_2021, num_tornados_2022, num_tornados_2023, num_tornados_2024) "
                  "VALUES (default, %(county_name)s, %(county_state)s, %(num_tornados_2014)s, %(num_tornados_2015)s, %(num_tornados_2016)s, %(num_tornados_2017)s, %(num_tornados_2018)s, %(num_tornados_2019)s, %(num_tornados_2020)s, %(num_tornados_2021)s, %(num_tornados_2022)s, %(num_tornados_2023)s, %(num_tornados_2024)s)")
    with open(file_path) as json_file:
        file_content = json_file.read()
        data = json.loads(file_content)
    print(data)
    for county in data:
        print(county)
        db_insert_data = {
            'county_name' : county,
            'county_state' : 'Wisconsin',
            'num_tornados_2014' : data[county]['2014'],
            'num_tornados_2015' : data[county]['2015'],
            'num_tornados_2016' : data[county]['2016'],
            'num_tornados_2017' : data[county]['2017'],
            'num_tornados_2018' : data[county]['2018'],
            'num_tornados_2019' : data[county]['2019'],
            'num_tornados_2020' : data[county]['2020'],
            'num_tornados_2021' : data[county]['2021'],
            'num_tornados_2022' : data[county]['2022'],
            'num_tornados_2023' : data[county]['2023'],
            'num_tornados_2024' : data[county]['2024']
        }
        cursor.execute(add_tornado_stats, db_insert_data)
        print('inserted data {db}'.format(db = db_insert_data))
        cnx.commit()

wi_counties = ['Buffalo','Trempealeau','Marinette','Sauk','Eau Claire','Crawford','Door','Juneau','Rusk','Adams','Iron','Ashland','Bayfield','Grant','Clark','Oneida','Fond du Lac','Calumet','Chippewa','Rock','Vernon','Racine','Kenosha','Walworth','Pierce','La Crosse','Kewaunee','Sheboygan','Lafayette','Polk','Douglas','Brown','Dane','Dodge','Green Lake','Sawyer','Portage','Dunn','Winnebago','Shawano','Jefferson','Jackson','Washington','Marathon','Barron','Iowa','Taylor','Menominee','Waushara','Washburn','Manitowoc','Columbia','Milwaukee','Outagamie','Marquette','Richland','Florence','Oconto','Waukesha','Wood','Price','Ozaukee','Waupaca','Pepin','St. Croix','Forest','Burnett','Monroe','Langlade','Green','Vilas','Lincoln']
years = ['2014','2015','2016','2017','2018','2019','2020','2021','2022','2023','2024']

# main

insert_json_file('C:\\Users\\seanr\\OneDrive\\Documents\\Home-Lab\\code\\tornado\\db-scripts\\wi\\11-22-24_Complete-WI-Tornado-Stats.json')