import requests
import os

# https://www.weather.gov/source/mpx/TornadoStats/minnesotaTornadoes2010.xml

os.chdir("C:/Users/seanr/OneDrive/Documents/Home-Lab/tornado_data/mn")

for i in range(2010, 2021):
    url = f'https://www.weather.gov/source/mpx/TornadoStats/minnesotaTornadoes{i}.xml'
    response = requests.get(url)
    with open(f'mn_tornadoes_{i}.xml', 'wb') as f:
        f.write(response.content)
    print(f'File saved: mn_tornadoes_{i}.xml')