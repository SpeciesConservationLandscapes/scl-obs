import pandas as pd
import numpy as np
import os

# Paths
PROJECT_DIR = r'C:\Users\jesse\PycharmProjects\scl-obs\tiger'
DATA_DIR = r'C:\Users\jesse\Documents\wcs_tiger\data'
UNFORMATTED_DIR = os.path.join(DATA_DIR, 'unformatted_data')
FORMATTED_DIR = os.path.join(DATA_DIR, 'tip_formatted_data')
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'ingest_template')

# Import data and TIP templates
data = pd.read_excel(os.path.join(UNFORMATTED_DIR, 'CamComAll_30min MASTER_Hukaung.xls'))
ct_deployment = pd.read_csv(os.path.join(TEMPLATE_DIR, 'tiger observation entry CT deployments latlon.csv'), header=0)
ct_observation = pd.read_csv(os.path.join(TEMPLATE_DIR, 'tiger observation entry CT observations.csv'), header=0)
prey_list = pd.read_csv(os.path.join(PROJECT_DIR, 'prey_list', 'prey_list.csv'))

reference = 'Naing, Hla, et al. “Assessing Large Mammal and Bird Richness from Camera-Trap Records in the Hukaung ' \
            'Valley of Northern Myanmar.” RAFFLES BULLETIN OF ZOOLOGY, vol. 63, Dec. 2015, pp. 376–88. '



# CT Deployment
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

# drop last row of column sums from data frame
data.drop(data.tail(1).index, inplace=True)

# Populate CT deployment template
ct_deployment['project ID'] = data['StudyPeriod']
ct_deployment['deployment ID'] = data['CamPositionID']
ct_deployment['camera latitude'] = data['LatNDeg']
ct_deployment['camera longitude'] = data['LongEDeg']
ct_deployment['country'] = 'Myanmar'
ct_deployment['name of observer/PI'] = 'Hla Naing'
ct_deployment['organizational affiliation'] = 'WCS'
ct_deployment['email address'] = 'hnaing@wcs.org'
ct_deployment['reference'] = reference
ct_deployment['deployment date/time'] = pd.to_datetime(data['DateSet'], errors='coerce')
ct_deployment['pickup date/time'] = pd.to_datetime(data['DateRetrieved'], errors='coerce')

# drop duplicate rows for deployment data frame
ct_deployment.drop_duplicates(subset=['deployment ID',
                                      'deployment date/time',
                                      'camera latitude',
                                      'camera longitude'], inplace=True)

ct_deployment.dropna(subset=['deployment date/time', 'pickup date/time'], inplace=True)

# prey lists
large_prey = prey_list[prey_list['prey type'].eq('large prey')]
small_prey = prey_list[prey_list['prey type'].eq('small prey')]
livestock = prey_list[prey_list['prey type'].isin(['large livestock', 'small livestock'])]

# list of column names that are also species in the prey list
species = [s for s in data.columns.tolist() if s in prey_list.Species.tolist()]

# check prey of each camera deployment
for i in ct_deployment.index:
    sp = 0
    lp = 0
    ls = 0
    camera_id = ct_deployment['deployment ID'][i]
    # print(camera_id)

    # check if observed species is in prey list and set prey values in ct deployment

    for s in species:
        observation = data.loc[data['CamPositionID'] == camera_id, s].iloc[0]
        # prey_type = prey_list.loc[prey_list['Species'] == s, 'prey type'].iloc[0]

        if s in small_prey['Species'].tolist() and lp == 0 and observation > 0:
            sp = 1
        if s in large_prey['Species'].tolist() and lp == 0 and observation > 0:
            lp = 1
        if s in livestock['Species'].tolist() and ls == 0 and observation > 0:
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

ct_observation['project ID'] = data['StudyPeriod']
ct_observation['deployment ID'] = data['CamPositionID']
ct_observation['observation date/time'] = pd.to_datetime(data['DateSet'])
ct_observation['# adults sex unknown'] = data['Tiger']
ct_observation['# adult males'] = 0
ct_observation['# adult females'] = 0
ct_observation['# Subadults (either sex - 1-2 years old)'] = 0
ct_observation['# cubs (either sex - 1-12 month old)'] = 0


# filter on tiger detections
ct_observation = ct_observation[ct_observation['# adults sex unknown'] == 1]

# save data frames to CSV

# drop duplicates - each row should be an instance of a unique camera id, location, deployment time
# ct_deployment.drop_duplicates(subset=['deployment ID', 'deployment date/time'], inplace=True)
# ct_deployment.dropna(subset=['deployment date/time'], inplace=True)

ct_deployment_csv = os.path.join(FORMATTED_DIR,
                                 'CamComAll_30min MASTER_Hukaung_ct_deployments_latlon.csv')
ct_deployment.to_csv(ct_deployment_csv, index=False)
#
ct_observation_csv = os.path.join(FORMATTED_DIR,
                                 'CamComAll_30min MASTER_Hukaung_ct_observations.csv')
ct_observation.to_csv(ct_observation_csv, index=False)
