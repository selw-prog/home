import requests
import os
import pandas as pd
import geopandas as gpd
import tkinter as Tk
import matplotlib.pyplot as plt
from lxml import etree
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

root = Tk.Tk()
canvas = None

def get_tornado_data(year:str) -> dict:
    tornado_data = {}
    url = 'https://www.weather.gov/source/mpx/TornadoStats/minnesotaTornadoes{y}.xml'.format(y = year) # seems like they don't have data avail past 2010
    raw = requests.get(url)
    root = etree.fromstring(raw.content)
    data = []
    for child in root.iterchildren():
        data.append(dict(child.attrib))
    counties = {}
    for event in data:
        if ',' in event['counties']:
            for c in event['counties'].split(','):
                county = c.strip()
                if county in counties.keys():
                    counties[county] += 1
                else:
                    counties[county] = 1
        else:
            county = event['counties'].strip()
        if county in counties.keys():
            counties[county] += 1
        else:
            counties[county] = 1
    tornado_data[year] = counties
    return tornado_data

def generate_map(year:str):
    gdf = gpd.read_file(os.getcwd()+'/cb_2023_us_county_500k') # get geodataframe, source https://www2.census.gov/geo/tiger/GENZ2023/gdb/
    gdf = gdf[gdf.STATE_NAME == 'Minnesota']
    tornado_df = pd.DataFrame.from_dict(get_tornado_data(year))
    gdf = gdf.merge(tornado_df, how='left', left_on='NAME', right_index = True)
    gdf.loc[gdf[year].isnull(),year] = 0 # set all NaN values to 0 for plotting
    return gdf

def update(*args):
    global canvas
    if canvas: 
        canvas.get_tk_widget().pack_forget()
    fig, ax = plt.subplots()
    plt.axis('off')
    plt.title('Tornado Statistics by County')
    canvas = FigureCanvasTkAgg(fig, master = root)
    canvas.get_tk_widget().grid(row = 0, column = 1)
    for select in option_list.curselection():
        map = generate_map(option_list.get(select))
        map.plot(ax = ax,column = option_list.get(select),cmap = 'OrRd',edgecolor = 'black',legend = True)


# master tkinter window
root.geometry( "700x500" )
# dropdown menu with years
select_frame = Tk.LabelFrame(master = root, text = 'Year Selection').grid(row = 0, column = 0)
options = ['2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021']
option_list = Tk.Listbox(master = root, selectmode = 'single')
option_list.grid(row = 0, column = 0)
for item in range(len(options)):
    option_list.insert(item, options[item])
update_button = Tk.Button(master = root, text = 'Update Map', command = update).grid(row = 1, column = 0)
root.mainloop()