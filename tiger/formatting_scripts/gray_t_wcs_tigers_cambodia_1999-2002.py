import pandas as pd
import numpy as np
import os
import pyproj

# Paths
PROJECT_DIR = r'C:\Users\jesse\PycharmProjects\scl-obs\tiger'
DATA_DIR = r'C:\Users\jesse\Documents\wcs_tiger\data'
UNFORMATTED_DIR = os.path.join(DATA_DIR, 'unformatted_data')
FORMATTED_DIR = os.path.join(DATA_DIR, 'tip_formatted_data')
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'ingest_template')

data = pd.read_csv(os.path.join(UNFORMATTED_DIR, 'gray_t_wcs_tigers_cambodia_1999-2002_.csv'))
adhoc = pd.read_csv(os.path.join(TEMPLATE_DIR, 'tiger observation entry ad hoc latlon.csv'), header=0)
prey_list = pd.read_csv(os.path.join(PROJECT_DIR, 'prey_list', 'prey_list.csv'), header=0)

# convert from UTM to lat lon
proj_utm = pyproj.Proj("+proj=utm +zone=48, +north +ellps=WGS84 +datum=WGS84 +units=m +no_defs")
lon, lat = proj_utm(data['UTM East'].values, data['UTM North'].values, inverse=True)

# adhoc['country'] = data['Tiger Range Country']
# adhoc['name of observer/PI'] = 'Thomas Gray'
# adhoc['organizational affiliation'] = ''
# adhoc['email address'] = data['Publication Contact (email)']
adhoc['observation date'] = pd.to_datetime(data['DateRecorded'], errors='coerce')
adhoc['observation longitude'] = lon
adhoc['observation latitude'] = lat
adhoc['# adults sex unknown'] = data['Total']

print(adhoc)

adhoc_csv = os.path.join(FORMATTED_DIR, 'gray_t_wcs_tigers_cambodia_1999-2002_formatted.csv')
adhoc.to_csv(adhoc_csv, index=False)