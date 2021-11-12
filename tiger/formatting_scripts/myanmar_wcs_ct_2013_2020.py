import pandas as pd
import numpy as np
import os
import datetime as dt

# Paths
PROJECT_DIR = r'C:\Users\jesse\PycharmProjects\scl-obs\tiger'
DATA_DIR = r'C:\Users\jesse\Documents\wcs_tiger\data'
UNFORMATTED_DIR = os.path.join(DATA_DIR, 'unformatted_data')
FORMATTED_DIR = os.path.join(DATA_DIR, 'tip_formatted_data')
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'ingest_template')


# CT deployment template lat lon
# Columns: [country,
#           grid,
#           name of observer/PI,
#           organizational affiliation,
#           email address,
#           project ID,
#           deployment ID,
#           camera longitude,
#           camera latitude,
#           deployment date/time,
#           pickup date/time,
#           bait,
#           quiet period setting,
#           large prey,
#           small prey,
#           livestock,
#           notes]

# Import data and TIP templates
data = pd.read_csv(os.path.join(UNFORMATTED_DIR, 'CTrapData_Htamanthi2013-2020 & HukaungValley2017_WCSMyanmar_1.csv'))
ct_deployment = pd.read_csv(os.path.join(TEMPLATE_DIR, 'tiger observation entry CT deployments latlon.csv'), header=0)
ct_observation = pd.read_csv(os.path.join(TEMPLATE_DIR, 'tiger observation entry CT observations.csv'), header=0)
prey_list = pd.read_csv(os.path.join(PROJECT_DIR, 'prey_list', 'prey_list.csv'), header=0)

#  create unique IDs for each cemera deployment
# data['deployment ID'] = data['Camera ID'] + pd.to_datetime(data['Camera start operational date']).dt.strftime('%F') + data['Y (northing)'].map(str) + data['X (easting)'].map(str)
data['deployment ID'] = data['CT location'] + data['Camera ID']
data['Date.Time.Original'] = pd.to_datetime(data['Date.Time.Original'], errors='coerce')
data['Date.Time.Original'].fillna(pd.to_datetime(data['Date (DD/MM/YYYY)']+ ' ' + data['Time (HH:MM:SS)'], errors='coerce'), inplace=True)
# CT Deployment

# convert camera start operational time data format error
data.loc[(data['Camera start operational time'] == 'WY31730'), 'Camera start operational time'] = '00:00:00'

# Populate CT deployment template
ct_deployment['deployment ID'] = data['deployment ID']
ct_deployment['country'] = data['Country']
ct_deployment['name of observer/PI'] = 'Hla Naing'
ct_deployment['organizational affiliation'] = 'WCS'
ct_deployment['email address'] = 'hnaing@wcs.org'
ct_deployment['project ID'] = data["Year"].astype(str) + data['Project Name']
ct_deployment['camera latitude'] = data['Y (northing)']
ct_deployment['camera longitude'] = data['X (easting)']
ct_deployment['deployment date'] = pd.to_datetime(data['Camera start operational date'])
ct_deployment['deployment date/time'] = pd.to_datetime(data['Camera start operational date']+ ' ' + data['Camera start operational time'], errors='coerce')
ct_deployment['pickup date/time'] = pd.to_datetime(data['Camera collection date'] + ' ' + data['Camera collection time'], errors='coerce')
# drop duplicates - each row should be an instance of a unique camera id, location, deployment tim
ct_deployment.drop_duplicates(subset=['deployment ID',
                                      'deployment date',
                                      'camera latitude',
                                      'camera longitude'], inplace=True)

ct_deployment.drop(columns='deployment date', inplace=True)
ct_deployment.dropna(subset=['deployment date/time'], inplace=True)

# get prey lists
large_prey = prey_list[prey_list['prey type'].eq('large prey')]
small_prey = prey_list[prey_list['prey type'].eq('small prey')]
livestock = prey_list[prey_list['prey type'].isin(['large livestock', 'small livestock'])]

# check prey of each camera deployment
for i in ct_deployment.index:

    # prey type flags
    sp = 0
    lp = 0
    ls = 0

    camera_id = ct_deployment['deployment ID'][i]

    # list of unique species observed at camera deployment
    species = data[data['Camera ID'].eq(camera_id)].drop_duplicates(subset=['Species'])

    # if observed species is in prey list set prey values in ct deployment to 1
    for s in species['Species']:

        if s in small_prey['Species'].tolist() and lp == 0:
            sp = 1
        if s in large_prey['Species'].tolist() and lp == 0:
            lp = 1
        if s in livestock['Species'].tolist() and ls == 0:
            ls = 1
    ct_deployment.loc[ct_deployment['deployment ID'] == camera_id, 'large prey'] = lp
    ct_deployment.loc[ct_deployment['deployment ID'] == camera_id, 'small prey'] = sp
    ct_deployment.loc[ct_deployment['deployment ID'] == camera_id, 'livestock'] = ls


# CT observation template
# Columns ['project ID',
#          'deployment ID',
#          'observation date/time',
#          '# adult males',
#          '# adult females',
#          '# adults sex unknown',
#          '# Subadults (either sex - 1-2 years old)',
#          '# cubs (either sex - 1-12 month old)'],

ct_observation['project ID'] = data["Year"].astype(str) + data['Project Name']
# ct_observation['deployment ID'] = data['deployment ID']
ct_observation['deployment ID'] = data['deployment ID']
ct_observation['observation date/time'] = data['Date.Time.Original']
ct_observation['# adults sex unknown'] = np.where(data['Latin Name'] == 'Panthera tigris', 1, 0)

# drop observations without tigers
ct_observation = ct_observation[ct_observation['# adults sex unknown'] == 1]

# save data frames to CSV
ct_deployment_csv = os.path.join(FORMATTED_DIR,
                                 'CTrapData_Htamanthi2013-2020 & HukaungValley2017_WCSMyanmar_ct_deployments_latlon.csv')
ct_deployment.to_csv(ct_deployment_csv, index=False)

ct_observation_csv = os.path.join(FORMATTED_DIR,
                                 'CTrapData_Htamanthi2013-2020 & HukaungValley2017_WCSMyanmar_ct_observations.csv')
ct_observation.to_csv(ct_observation_csv, index=False)

# taxon = ['Bird', 'Insect', 'Mammal', 'Mammal and Bird', 'Reptile']
#
# species_list = data[['Taxon', 'Species', 'Latin Name']].drop_duplicates()
# species_list = species_list[species_list.Taxon.isin(taxon)]
#
# PREY_LIST = r'C:\Users\jesse\PycharmProjects\wcs_tiger\prey_list'
# species_list.to_csv(os.path.join(PREY_LIST,
#                               'CTrapData_Htamanthi2013-2020 & HukaungValley2017_WCSMyanmar_species_list.csv'), index=False)