import mysql.connector
from dotenv import dotenv_values

# schema 
# county(countyID INT, county VARCHAR, state VARCHAR, geometry TEXT) - PK countyID
# tornado (countyID INT, year INT, numTornados INT) - PK (countyID, year) - FK countyID references county(countyID)


sqlserver_config = dotenv_values('.env')
cnx = mysql.connector.connect(user = sqlserver_config['USERNAME'], password = sqlserver_config['PASSWORD'],
                              host = sqlserver_config['IPADDRESS'], database = sqlserver_config['DATABASE'])
cursor = cnx.cursor()

add_mn_county = ("INSERT INTO county "
              "(countyID, county, state, geometry) "
              "VALUES (default,%(county)s, %(state)s, %(geometry)s)")

test_data = {
    'county' : 'Rice',
    'state' : 'Minnesota',
    'geometry' : 'test data'
}

cursor.execute(add_mn_county, test_data)
cnx.commit()
cursor.close()
cnx.close()