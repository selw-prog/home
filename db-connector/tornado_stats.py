import mysql.connector
from dotenv import dotenv_values

# schema 
# year INT NOT NULL, state VARCHAR(20) NOT NULL, county VARCHAR(20) NOT NULL, numTornados INT NOT NULL, 
# PK (year,state,county) 


sqlserver_config = dotenv_values('.env')
cnx = mysql.connector.connect(user = sqlserver_config['USERNAME'], password = sqlserver_config['PASSWORD'],
                              host = sqlserver_config['IPADDRESS'], database = sqlserver_config['DATABASE'])
cursor = cnx.cursor()

add_tornado_stats = ("INSERT INTO tornado "
              "(year, state, county, numTornados) "
              "VALUES (%(year)s,%(state)s, %(county)s, %(numTornados)s)")

test_data = {
    'year' : '1',
    'state' : 'Minnesota',
    'county' : 'Rice',
    'numTornados' : 10
}

cursor.execute(add_tornado_stats, test_data)
cnx.commit()
cursor.close()
cnx.close()