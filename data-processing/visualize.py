import logging
import os
import time
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from tkinter import filedialog

# Set up logging
log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
log_file = 'C:\\Users\\seanr\\OneDrive\\Documents\\Logs\\Python\\{time}_{file_name}.log'.format(time=time.strftime("%Y%m%d-%H%M%S"), file_name=os.path.basename(__file__))
logging.basicConfig(level=logging.INFO, filename = log_file, format = log_format)
time=time.strftime("%Y%m%d-%H%M%S") # Get the current time to reference in file names

file_path = filedialog.askopenfile()
logging.info('Processing files in directory {d}'.format(d = file_path))

df = pd.read_csv(file_path)
state_group = df.groupby('STATE')
state_counts = state_group.size()
state_counts.plot(kind='bar')
plt.title('Number of Strings per Category')
plt.xlabel('Category')
plt.ylabel('Number of Strings')
plt.show()