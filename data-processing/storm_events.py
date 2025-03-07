import logging
import os
import time
import pandas as pd
from pathlib import Path
from tkinter import filedialog

# Set up logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_file = 'C:\\Users\\seanr\\OneDrive\\Documents\\Logs\\Python\\{time}_{file_name}.log'.format(time=time.strftime("%Y%m%d-%H%M%S"), file_name=os.path.basename(__file__))
logging.basicConfig(level=logging.INFO, filename = log_file, format = log_format)
time=time.strftime("%Y%m%d-%H%M%S") # Get the current time to reference in file names

def process_chunk(chunk):
    # Filter out rows with 'Tornado' in the 'EVENT_TYPE' column
    tornadoes = chunk[chunk['EVENT_TYPE'].eq('Tornado')]
    return tornadoes

# Select the file to process
file_dir = filedialog.askdirectory()
logging.info('Processing files in directory {d}'.format(d = file_dir))

# Process file in chunks and save to a new file
header=True
for file in os.listdir(file_dir):
    logging.info('Processing file {f}'.format(f=file))
    reader = pd.read_csv(Path(file_dir, file), chunksize=1000)
    for i, chunk in enumerate(reader):
        logging.info('Processing chunk {n}'.format(n = i+1))
        data = process_chunk(chunk)
        logging.info(data.head())
        data.to_csv('C:\\Users\\seanr\\OneDrive\\Documents\\Home-Lab\\tornado_data\\stormevents-db\\processed\\{t}_tornadoes.csv'.format(t = time),
                    mode='a', header=header)
        header=False