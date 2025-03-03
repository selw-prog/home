import requests
import os

# https://www.weather.gov/source/dmx/IowaTors/2023tors.kml

os.chdir("C:/Users/seanr/OneDrive/Documents/Home-Lab/tornado_data/ia")

for i in range(2012, 2023):
    url = f'https://www.weather.gov/source/dmx/IowaTors/{i}tors.kml'
    response = requests.get(url)
    with open(f'ia_tornadoes_{i}.kml', 'wb') as f:
        f.write(response.content)
    print(f'File saved: ia_tornadoes_{i}.xml')