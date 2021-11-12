import pandas as pd
import numpy as np
import os

# Paths
PROJECT_DIR = r'C:\Users\jesse\PycharmProjects\scl-obs\tiger'
DATA_DIR = r'C:\Users\jesse\Documents\wcs_tiger\data'
UNFORMATTED_DIR = os.path.join(DATA_DIR, 'unformatted_data')
FORMATTED_DIR = os.path.join(DATA_DIR, 'tip_formatted_data')
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'ingest_template')

area_validation_save_flag = True

data = pd.read_excel(os.path.join(UNFORMATTED_DIR, 'TigerDensityCompilation_V_3.2.xlsx'), header=1)
cell_area = pd.read_csv(os.path.join(DATA_DIR, 'abishek_data_summary', 'tiger_density_cell_area_overlap.csv'), header=0)
grid_contains_point = pd.read_csv(
    os.path.join(DATA_DIR, 'abishek_data_summary', 'TigerDensity_grid_contains_point.csv'))
polygon_area = pd.read_csv(os.path.join(DATA_DIR, 'abishek_data_summary', 'TigerDesnity_polygon_area.csv'), header=0)

data_trap_area = data[['Trap area (Sq. Km)', 'Record ID']]

# cell area
zone_1 = 16
zone_2 = 256
zone_3 = 1024

cell_area = cell_area[cell_area['percent_overlap'] > 50]

# concatenate cells with majority overlap and cells with containing points, then drop duplicates
cell_area = pd.concat([cell_area, grid_contains_point]).drop_duplicates(subset=['RecordID', 'gridid'])

# assign area for cell based on zone ID
cell_area['cell_area'] = 0
cell_area['cell_area'] = np.where(cell_area['zone'] == 1, zone_1, cell_area['cell_area'])
cell_area['cell_area'] = np.where(cell_area['zone'] == 2, zone_2, cell_area['cell_area'])
cell_area['cell_area'] = np.where(cell_area['zone'] == 3, zone_3, cell_area['cell_area'])

# sum cell area for each record
cell_area = cell_area.groupby('RecordID', as_index=False).agg({'cell_area': 'sum'})

# tiger density summary columns
columns = ['Record ID',
           'Study ID',
           'Tiger Range Country',
           'Site Name',
           'Year of publication',
           'Trap area (Sq. Km)'
          ]

data = data[columns]

data = data.merge(cell_area, left_on='Record ID', right_on='RecordID', how='left').drop(columns='RecordID')
data = data.merge(polygon_area, left_on='Record ID', right_on='RecordID', how='left').drop(columns='RecordID')
data.rename(columns={'area' : 'shape_area'}, inplace=True)
data.drop_duplicates(inplace=True)

data['area_diff'] = data['cell_area'] - pd.to_numeric(data['Trap area (Sq. Km)'], errors='coerce').round(decimals=2)
data['percent_diff'] = (data['area_diff'] / pd.to_numeric(data['Trap area (Sq. Km)'], errors='coerce')
                        * 100).round(decimals=0)

if area_validation_save_flag is True:
    data.to_csv(os.path.join(DATA_DIR, 'abishek_data_summary', 'tiger_density_area_validation.csv'), index=False)
    print(data.head())
