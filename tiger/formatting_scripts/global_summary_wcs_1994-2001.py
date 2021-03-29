import pandas as pd
import numpy as np
import os

# Paths
PROJECT_DIR = r'C:\Users\jesse\PycharmProjects\scl-obs'
DATA_DIR = r'C:\Users\jesse\Documents\wcs_tiger\data'
UNFORMATTED_DIR = os.path.join(DATA_DIR, 'unformatted_data')
FORMATTED_DIR = os.path.join(DATA_DIR, 'tip_formatted_data')
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'ingest_template')

# Import data and TIP templates
data = pd.read_excel(os.path.join(UNFORMATTED_DIR, 'TigerPointData_proc.6_headerfix.xls'), header=0)
adhoc = pd.read_csv(os.path.join(TEMPLATE_DIR, 'tiger observation entry ad hoc latlon.csv'), header=0)
ct_observation = pd.read_csv(os.path.join(TEMPLATE_DIR, 'tiger observation entry CT observations.csv'), header=0)
prey_list = pd.read_csv(os.path.join(PROJECT_DIR, 'prey_list', '2021-03-15_prey_list.csv'))

# data.columns = data.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
print(data.columns.values.tolist())



adhoc['country'] = data['Country']
adhoc['name of observer/PI'] = data['Researcher(s)']
adhoc['organizational affiliation'] = 'WCS'
adhoc['email address'] = 'hnaing@wcs.org'
adhoc['observation date'] = pd.to_datetime(data['Date of Last Observation'], errors='coerce')
adhoc['observation longitude'] = data['Longitude']
adhoc['observation latitude'] = data['Latitude']
adhoc['# adults sex unknown'] = ''

# Location Method
adhoc['GPS'] = np.where(data['GPS'] > 1, 1, 0)
adhoc['Telemetry Fix'] = np.where(data['Telemetry Fix'] >= 1, 1, 0)
adhoc['Map and Compass'] = np.where(data['Map and Compass'] >= 1, 1, 0)
adhoc['Dead Reckoning (on map)'] = np.where(data['Dead Reckoning'] >= 1, 1, 0)

# Observation
# print(data['Photograph'].dtypes())
data = data.replace(r'^\s*$', np.NaN, regex=True)

adhoc['Photograph'] = np.where(data['Photograph'] >= 1, 1, 0)
adhoc['Firsthand Sighting'] = np.where(data['Firsthand Sighting'] >= 1, 1, 0)
adhoc['Tracks'] = np.where(data['Tracks'] >= 1, 1, 0)
adhoc['Scat'] = np.where(data['Scat'] >= 1, 1, 0)
adhoc['Telemetry'] = np.where(data['Telemetry'] >= 1, 1, 0)
adhoc['Tiger Mortality'] = np.where(data['Tiger Mortality'] >= 1, 1, 0)
adhoc['Tiger Kill'] = np.where(data['Tiger Kill'] >= 1, 1, 0)
adhoc['Vocalizations Heard'] = np.where(data['Heard'] >= 1, 1, 0)
adhoc['Observation Type Report'] = np.where(data['Report (high confidence)'] >= 1, 1, 0)

adhoc['# adults sex unknown'] = data['# adults sex unknown'].fillna(0).astype(dtype=int)
adhoc['# adult  females'] = data['# adult females'].fillna(0).astype(dtype=int)
adhoc['# cubs (either sex - 1-12 month old)'] = data['# cubs (either sex - 1-12 month old)'].fillna(0).astype(dtype=int)
adhoc['notes'] = data['Notes']

adhoc_csv = os.path.join(FORMATTED_DIR, 'TigerPointData_proc.6_headerfix_formatted.csv')
adhoc.to_csv(adhoc_csv, index=False)