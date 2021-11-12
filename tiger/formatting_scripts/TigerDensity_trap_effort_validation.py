import pandas as pd
import numpy as np
import os

# Paths
PROJECT_DIR = r'C:\Users\jesse\PycharmProjects\scl-obs\tiger'
DATA_DIR = r'C:\Users\jesse\Documents\wcs_tiger\data'
UNFORMATTED_DIR = os.path.join(DATA_DIR, 'unformatted_data')
FORMATTED_DIR = os.path.join(DATA_DIR, 'tip_formatted_data')
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'ingest_template')

# Save flag
trap_effort_validation_save_flag = True

data = pd.read_excel(os.path.join(UNFORMATTED_DIR, 'TigerDensityCompilation_V_3.2.xlsx'), header=1)

# tiger density summary columns
columns = ['Record ID',
           'Study ID',
           'Tiger Range Country',
           'Site Name',
           'Year of publication',
           'Trap area (Sq. Km)',
           'Sampling Start Date',
           'Sampling End Date',
           'No. of trap location',
           'Trap effort'
           ]

data = data[columns]
data['Sampling Start Date'] = pd.to_datetime(data['Sampling Start Date'], errors='coerce')
data['Sampling End Date'] = pd.to_datetime(data['Sampling End Date'], errors='coerce')
data['sampling_length'] = (data['Sampling End Date'] - data['Sampling Start Date']) / np.timedelta64(1, 'D')
data['estimated_trap_effort'] = data['sampling_length'] * data['No. of trap location']
data['effort_diff'] = pd.to_numeric(data['Trap effort'], errors='coerce') - data['estimated_trap_effort']
data['percent_diff'] = (data['effort_diff'] / data['Trap effort'] * 100)

if trap_effort_validation_save_flag is True:
    data.to_csv(os.path.join(DATA_DIR, 'abishek_data_summary', 'tiger_density_trap_effort_validation.csv'), index=False)
    print(data.head())

# verified absence
