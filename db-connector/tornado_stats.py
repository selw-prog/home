import mysql.connector
from dotenv import dotenv_values

# schema 
# year INT NOT NULL, state VARCHAR(20) NOT NULL, county VARCHAR(20) NOT NULL, numTornados INT NOT NULL, 
# PK (year,state,county) 


sqlserver_config = dotenv_values('.env')
cnx = mysql.connector.connect(user = sqlserver_config['USERNAME'], password = sqlserver_config['PASSWORD'],
                              host = sqlserver_config['IPADDRESS'], database = sqlserver_config['DATABASE'])

add_county = ("INSERT INTO county "
              "(year, state, county, numTornados) "
              "VALUES ({y}, {s}, {c}, {nT})".format())

