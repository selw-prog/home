import cv2
import pytesseract
import mysql.connector
import pandas as pd

from dotenv import dotenv_values
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'

# detect tornado data in table
img_cv = cv2.imread('2024WiTorEvents.jpg')
img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
detected_info = pytesseract.image_to_string(img_rgb)
# get all wisconsin counties
sqlserver_config = dotenv_values('../.env')
cnx = mysql.connector.connect(user = sqlserver_config['USERNAME'], password = sqlserver_config['PASSWORD'],
                              host = sqlserver_config['IPADDRESS'], database = sqlserver_config['DATABASE'])
cursor = cnx.cursor()
query = ("SELECT countyID,county,state FROM county WHERE state = 'Wisconsin'")
cursor.execute(query)
df_wi_counties = pd.DataFrame(cursor, columns = cursor.column_names)
# identify counties and how many instances of a given county exist within detected_info
tornado_stats = {}
total_count = 0
for county in df_wi_counties['county']:
    num_instances = detected_info.count(county)
    if num_instances != 0:
        tornado_stats[county] = num_instances
        total_count = total_count + num_instances
# print before all changes made
for county in tornado_stats:
    print('{c} : {s}'.format(c = county, s = tornado_stats[county]))
# remove stats associated with Green and Washington - these are erroneous
tornado_stats['Buffalo'] = tornado_stats['Buffalo'] - 1
del(tornado_stats['Green'])
del(tornado_stats['Washington'])
print()
# add in stats for missing rows 1 and 2
missing_county_entries = ['Green','Rock','Dane','Jefferson']
for county in missing_county_entries:
    if county in tornado_stats.keys():
        tornado_stats[county] = tornado_stats[county] + 1
    else:
        tornado_stats[county] = 1
# print after all changes made
total_count = 0
for county in tornado_stats:
    print('{c} : {s}'.format(c = county, s = tornado_stats[county]))
    total_count = total_count + tornado_stats[county]
print(total_count)
# stats validated and ready to insert into database
