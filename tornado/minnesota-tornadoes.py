import requests
import os
import pandas as pd
import geopandas as gpd
import tkinter as Tk
import matplotlib.pyplot as plt
from lxml import etree
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# CONSTANTS
YEARS = ['2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021']
TORNADO_DATA = {}

def get_tornado_data() -> gpd.GeoDataFrame:
    '''
    Processes .xml files from weather.gov for all years specified in YEARS. 
    '''
    for year in YEARS:
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
        TORNADO_DATA[year] = counties
    gdf = gpd.read_file(os.getcwd()+'/cb_2023_us_county_500k') # get geodataframe, source https://www2.census.gov/geo/tiger/GENZ2023/gdb/
    gdf = gdf[gdf.STATE_NAME == 'Minnesota']
    tornado_df = pd.DataFrame.from_dict(TORNADO_DATA)
    gdf = gdf.merge(tornado_df, how='left', left_on='NAME', right_index = True)
    for year in YEARS:
        gdf.loc[gdf[year].isnull(),year] = 0 # set all NaN values to 0 for plotting
    return gdf

def update(*args):
    plt.close()
    gdf['YEAR_SUM'] = 0
    global canvas # should this really be here?
    if canvas: 
        canvas.get_tk_widget().pack_forget()
    fig, ax = plt.subplots()
    plt.axis('off')
    plt.title('Tornado Statistics by County')
    canvas = FigureCanvasTkAgg(fig, master = root)
    canvas.get_tk_widget().grid(row = 0, column = 1)
    for select in option_list.curselection():
        gdf['YEAR_SUM'] = gdf['YEAR_SUM'] + gdf[option_list.get(select)]
    gdf['YEAR_SUM'] = gdf['YEAR_SUM'].astype(int)
    gdf.plot(ax = ax,column = 'YEAR_SUM',cmap = 'OrRd',edgecolor = 'black',legend = True)


# get all data
gdf = get_tornado_data()
# master tkinter window
root = Tk.Tk()
canvas = None 
root.geometry( "700x500" )
# dropdown menu with years
select_frame = Tk.Frame(master = root).grid(row = 0, column = 0)
option_list = Tk.Listbox(master = root, selectmode = 'multiple')
option_list.grid(row = 0, column = 0, pady = 2)
for item in range(len(YEARS)):
    option_list.insert(item, YEARS[item])
update_button = Tk.Button(master = root, text = 'Update Map', command = update).grid(row = 1, column = 0)
option_list.select_set(0)
update()
root.mainloop()