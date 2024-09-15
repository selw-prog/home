import cv2
import pytesseract
import mysql.connector
import logging
import os
import pandas as pd

from pathlib import Path
from datetime import datetime
from dotenv import dotenv_values
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
log_filename = datetime.now().strftime('%Y_%m_%H_%M_wi_data_insert.log')
log_path = Path(r'C:\Users\seanr\Documents\Logs\Python')
logging.basicConfig(filename='{p}\{f}'.format(p = log_path, f = log_filename), encoding='utf-8', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')

sqlserver_config = dotenv_values('../.env')
cnx = mysql.connector.connect(user = sqlserver_config['USERNAME'], password = sqlserver_config['PASSWORD'],
                              host = sqlserver_config['IPADDRESS'], database = sqlserver_config['DATABASE'])
cursor = cnx.cursor()

def add_wi_tornado_stats_to_db(tornado_df):
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
            'year' : 2024,
            'numTornados' : row['numTornados']
        }
        logging.info(db_insert_data)
        cursor.execute(add_tornado_stats, db_insert_data)
        cnx.commit()
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

# main
image_repo_path = r'C:\Users\seanr\Documents\Home-Lab\code\tornado\db-scripts\wi\new'
for file in os.listdir(image_repo_path):
    filename = os.path.join(image_repo_path, file)
    logging.info('Processing file {f}.'.format(f = filename))
    img_cv = cv2.imread(filename)
    logging.info('Using {f} as input.'.format(f = filename))
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    detected_info = pytesseract.image_to_string(img_rgb)
    query = ("SELECT countyID,county,state FROM county WHERE state = 'Wisconsin'")
    cursor.execute(query)
    logging.info('Executed {q} against {db}.'.format(q = query, db = sqlserver_config['IPADDRESS']))
    df_wi_counties = pd.DataFrame(cursor, columns = cursor.column_names)
    # identify counties and how many instances of a given county exist within detected_info
    tornado_stats = {}
    total_count = 0
    for county in df_wi_counties['county']:
        num_instances = detected_info.count(county)
        if num_instances != 0:
            tornado_stats[county] = num_instances
            total_count = total_count + num_instances
    # print before any corrections are made
    for county in tornado_stats:
        logging.info('COUNTY NAME : {c} --> NUM_TORNADOS : {s}'.format(c = county, s = tornado_stats[county]))
    ## make all adjustments based on .jpg being ingested ##
    #tornado_stats['Green'] = tornado_stats['Green'] - 1
    total_count = 0
    for county in tornado_stats:
        logging.info('COUNTY NAME : {c} --> NUM_TORNADOS : {s}'.format(c = county, s = tornado_stats[county]))
        total_count = total_count + tornado_stats[county]
    logging.info('Total number of tornados found in this file : {c}.'.format(c = total_count))
    # stats validated and ready to insert into database
    tornado_df = pd.DataFrame.from_dict(tornado_stats, orient = 'index', columns = ['numTornados'])
    logging.info('File processing {f} completed.'.format(f = filename))