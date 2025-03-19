import pandas as pd
import csv
import sqlalchemy
import mysql
from pathlib import Path
from dotenv import dotenv_values

# Schema 
# tornado (id INT, event_date DATE, state VARCHAR(100), county VARCHAR(100), scale VARCHAR(3), location VARCHAR(100)) - PK id
# sample : INSERT INTO tornado VALUES (1, '2021-06-07', 'MN', 'Hennepin', 'EF0', 'Minneapolis')

sqlserver_config = dotenv_values('C:\\Users\seanr\\OneDrive\\Documents\\Home-Lab\\code\\data-processing\\sql.env')
engine = sqlalchemy.create_engine('mysql+mysqlconnector://{username}:{password}@{ipaddress}/{database}'.format(
    username=sqlserver_config['USERNAME'], password=sqlserver_config['PASSWORD'], ipaddress=sqlserver_config['IPADDRESS'], database=sqlserver_config['DATABASE']))
with engine.connect() as conn:
    result = conn.execute(sqlalchemy.text("SELECT * FROM tornado"))
    print(result.all())