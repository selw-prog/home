import pandas as pd
import csv
import sqlalchemy
import mysql
import logging
import time
import os
from pathlib import Path
from dotenv import dotenv_values

# Schema 
# tornado (id INT, event_date DATE, state VARCHAR(100), county VARCHAR(100), scale VARCHAR(3), location VARCHAR(100)) - PK id
# sample : INSERT INTO tornado VALUES (1, '2021-06-07', 'MN', 'Hennepin', 'EF0', 'Minneapolis')

# Set up logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_file = 'C:\\Users\\seanr\\OneDrive\\Documents\\Logs\\Python\\{time}_{file_name}.log'.format(time=time.strftime("%Y%m%d-%H%M%S"), file_name=os.path.basename(__file__))
logging.basicConfig(level=logging.INFO, filename = log_file, format = log_format)
time=time.strftime("%Y%m%d-%H%M%S") # Get the current time to reference in file names

dtype_mapping = {
    'id': sqlalchemy.Integer,
    'event_date': sqlalchemy.Date,
    'state': sqlalchemy.String(100),
    'county': sqlalchemy.String(100),
    'scale': sqlalchemy.String(3),
    'location': sqlalchemy.String(100)
}

def output(string:str):
    print(string)
    logging.info(string)

csv_file = Path(
    'C:\\Users\\seanr\\OneDrive\\Documents\\Home-Lab\\tornado_data\\stormevents-db\\processed\\20250307-204641_tornadoes_edited.csv')
sqlserver_config = dotenv_values('C:\\Users\seanr\\OneDrive\\Documents\\Home-Lab\\code\\data-processing\\sql.env')
engine = sqlalchemy.create_engine('mysql+mysqlconnector://{username}:{password}@{ipaddress}/{database}'.format(
    username=sqlserver_config['USERNAME'], password=sqlserver_config['PASSWORD'], ipaddress=sqlserver_config['IPADDRESS'], database=sqlserver_config['DATABASE']))
csv_df = pd.read_csv(csv_file)
with engine.connect() as conn:
    output('Connected to database. Inserting data..')
    csv_df.to_sql('tornado', conn, if_exists='append', index=False, dtype = dtype_mapping)
    output('Insertion complete. Getting data now..')
    result = conn.execute(sqlalchemy.text("SELECT * FROM tornado"))
    output(result.all())