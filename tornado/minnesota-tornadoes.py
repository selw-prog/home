import requests
import os
import pandas as pd
import geopandas as gpd
import tkinter as Tk
import matplotlib.pyplot as plt
import mysql.connector
from lxml import etree
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dotenv import dotenv_values

# CONSTANTS
YEARS = ['2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','2021','2022','2023','2024'] # weather.gov site does not have data past 2010 available
#STATES = ['Minnesota','Iowa','Wisconsin']
TORNADO_DATA = {}

sqlserver_config = dotenv_values('.env')
cnx = mysql.connector.connect(user = sqlserver_config['USERNAME'], password = sqlserver_config['PASSWORD'],
                              host = sqlserver_config['IPADDRESS'], database = sqlserver_config['DATABASE'])
cursor = cnx.cursor()
query = ("SELECT county.countyID,county.county,county.state,county.geometry,tornado.year,tornado.numTornados FROM county INNER JOIN tornado ON county.countyID=tornado.countyID")
cursor.execute(query)
TORNADO_STATS_DF = pd.DataFrame(cursor, columns = cursor.column_names)
query = ("SELECT * FROM county")
cursor.execute(query)
df = pd.DataFrame(cursor, columns = cursor.column_names)
gs = gpd.GeoSeries.from_wkt(df['geometry'])
GDF = gpd.GeoDataFrame(df, columns = cursor.column_names, geometry = gs)

def update(*args):
    plt.close() # close previously open plot
    global canvas
    if canvas: 
        canvas.get_tk_widget().pack_forget()
    fig, ax = plt.subplots()
    plt.axis('off')
    plt.title('Tornado Statistics by County')
    canvas = FigureCanvasTkAgg(fig, master = root)
    canvas.get_tk_widget().pack(side = 'top')
    plot_gdf = GDF
    for select in year_option_list.curselection():
        filtered_stats = TORNADO_STATS_DF[TORNADO_STATS_DF.year == int(year_option_list.get(select))][['countyID','numTornados']]
        filtered_stats = filtered_stats.rename(columns = {'numTornados' : 'numTornados_{year}'.format(year = year_option_list.get(select))})
        plot_gdf = plot_gdf.merge(filtered_stats, on = 'countyID', how = 'left')
    plot_gdf['YEAR_SUM'] = plot_gdf[plot_gdf.columns[plot_gdf.columns.str.startswith('numTornados')]].sum(axis = 1)
    plot_gdf.plot(ax = ax,column = 'YEAR_SUM',cmap = 'OrRd',edgecolor = 'black',legend = True)
    # refreshing top 5 table
    for widget in top_5.winfo_children():
        widget.destroy()
    top_5_data_table = Tk.Frame(master = top_5)
    top_5_data_table.pack(side = 'top')
    top_5_counties = plot_gdf.sort_values('YEAR_SUM', ascending = False).head(5)[['county','YEAR_SUM']]
    county_header_label = Tk.Label(master = top_5_data_table, text = 'County Name', font = ('Helvectica', 9, 'bold')).grid(row = 0, column = 0)
    tornado_count_header_label = Tk.Label(master = top_5_data_table, text = 'Tornado Count', font = ('Helvectica', 9, 'bold')).grid(row = 0, column = 1)
    row_count = 1
    for index, row in top_5_counties.iterrows():
        county_name_label = Tk.Label(master = top_5_data_table, text = row.iloc[0], font = ('Helvectica', 9)).grid(row = row_count, column = 0) # county name
        tornado_count_label = Tk.Label(master = top_5_data_table, text = row.iloc[1], font = ('Helvectica', 9)).grid(row = row_count, column = 1) # tornado count
        row_count = row_count + 1

# master tkinter window
root = Tk.Tk()
root.title('Tornado Statistics')
canvas = None 
root.geometry('800x700')
top_5 = Tk.Frame(master = root)
top_5.pack(side = 'bottom')
# menu objects 
menu_frame = Tk.Frame(master = root)
menu_frame.pack(side = 'left')
# state option list #
#state_select_label = Tk.Label(master = menu_frame, text = 'State Selection').grid(row = 0, column = 0, pady = 2)
#state_option_list_frame = Tk.Frame(master = menu_frame)
#state_option_list_frame.grid(row = 1, column = 0, pady = 10)
#state_option_list = Tk.Listbox(master = state_option_list_frame, selectmode = 'extended') # extended mode doesn't work properly in Jupyter interactive window
#state_option_list.grid(row = 0, column = 0)
#for item in range(len(STATES)):
#    state_option_list.insert(item, STATES[item])
# year option list
year_select_label = Tk.Label(master = menu_frame, text = 'Year Selection').grid(row = 2, column = 0, pady = 2)
year_option_list_frame = Tk.Frame(master = menu_frame)
year_option_list_frame.grid(row = 3, column = 0, pady = 10)
year_option_list = Tk.Listbox(master = year_option_list_frame, selectmode = 'extended') # extended mode doesn't work properly in Jupyter interactive window
year_option_list.grid(row = 0, column = 0)
for item in range(len(YEARS)):
    year_option_list.insert(item, YEARS[item])
option_list_scrollbar = Tk.Scrollbar(master = year_option_list_frame, orient = 'vertical')
option_list_scrollbar.grid(row = 0, column = 1, sticky = 'ns')
option_list_scrollbar.config(command = year_option_list.yview)
year_option_list.config(yscrollcommand = option_list_scrollbar.set)
update_button = Tk.Button(master = menu_frame, text = 'Update Map', command = update).grid(row = 4, column = 0, pady = 2)
# default view
year_option_list.select_set(0)
update()
root.mainloop()