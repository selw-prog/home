import logging
import os
import time
import pandas as pd
from tkinter import filedialog

# Set up logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_file = 'C:\\Users\\seanr\\OneDrive\\Documents\\Logs\\Python\\{time}_{file_name}.log'.format(time=time.strftime("%Y%m%d-%H%M%S"), file_name=os.path.basename(__file__))
logging.basicConfig(level=logging.INFO, filename = log_file, format = log_format)

def process_chunk(chunk):
    # Filter out rows with 'Tornado' in the 'EVENT_TYPE' column
    tornadoes = chunk[chunk['EVENT_TYPE'].str.contains('Tornado')]
    return tornadoes

# Select the file to process
file_path = filedialog.askopenfilename()
logging.info(file_path)

# 
chunk_size = 1000
reader = pd.read_csv(file_path, chunksize=chunk_size)
for i, chunk in enumerate(reader):
    logging.info('Processing chunk {n}'.format(n = i+1))
    data = process_chunk(chunk)
    logging.info(data.head())
    if i == 5: 
        break