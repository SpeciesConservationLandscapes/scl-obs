import pandas as pd
import numpy as np
import os


# CI to se conversion
def high_ci_to_se(high_ci, est):
    return round(
                 (
                  np.sqrt(
                          np.exp(((np.log(high_ci) - np.log(est)) / 1.96) ** 2) - 1
                         ) * est
                 ), 2
                )


def low_ci_to_se(low_ci, est):
    return round(
                 (
                   np.sqrt(
                           np.exp(((np.log(est) - np.log(low_ci)) / 1.96) ** 2) - 1
                          ) * est
                 ), 2
                )


# Paths
PROJECT_DIR = r'C:\Users\jesse\PycharmProjects\scl-obs\tiger'
DATA_DIR = r'C:\Users\jesse\Documents\wcs_tiger\data'
UNFORMATTED_DIR = os.path.join(DATA_DIR, 'unformatted_data')
FORMATTED_DIR = os.path.join(DATA_DIR, 'tip_formatted_data')
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'ingest_template')

detection_review_save = False
detection_save = False
ad_hoc_save = True

# data = pd.read_excel(os.path.join(UNFORMATTED_DIR, 'TigerDensityCompilation_V_3.2.xlsx'), header=1)
data = pd.read_csv(os.path.join(UNFORMATTED_DIR, 'TigerDensityCompilation_V_3.2_org_affiliations.csv'), header=0)
ad_hoc = pd.read_csv(os.path.join(TEMPLATE_DIR, 'tiger observation entry ad hoc grid.csv'), header=0)

# grid_contains_point : all grid cells that contain a point from tiger site center point
# grid_majority : intersection of study area polygon and cell, where tiger site polygon overlaps more than 50% of cell
# grid_zone_overlap : list cells in tiger region grid that overlap
grid_contains_point = pd.read_csv(os.path.join(DATA_DIR, 'abishek_data_summary',
                                               'TigerDensity_grid_contains_point.csv'))
grid_majority = pd.read_csv(os.path.join(DATA_DIR, 'abishek_data_summary', 'TigerDensity_grid_majority.csv'))
grid_zone_overlap = pd.read_csv(os.path.join(DATA_DIR, 'abishek_data_summary',
                                             'tiger_region_grid_overlap.csv'), header=0)

data_year = pd.read_csv(os.path.join(DATA_DIR, 'abishek_data_summary',
                                     'TigerDensity_compilation_startyear_endyear.csv'), header=0)

data = data.merge(data_year, left_on='Record ID', right_on='RecordID').drop(columns='RecordID')

D_D1_conversion_factor = 0.81
D1_D2_conversion_factor = 0.89

# tiger density summary columns
columns = ['Record ID',
           'Study ID',
           'Tiger Range Country',
           'Site Name',
           'Year of publication',
           'Publication Title',
           'Publication Contact (Name)',
           'Publication Contact (email)',
           'organizational affiliation',
           'No. of trap location',
           'StartYear',
           'EndYear',
           'Sampling Start Date',
           'Sampling End Date',
           'Min No. Indivs (Mt+1)',
           'No. captures',
           'Trap effort',
           'Estimated D', 'SE (D)', 'Lower CI (D)', 'Upper CI (D)', 'Estimated N',
           'Estimated D.1', 'SE (D).1', 'Lower CI (D).1', 'Upper CI (D).1', 'Estimated N.1',
           'Estimated D.2', 'SD (D)', 'Lower HPD (D)', 'Upper HPD (D)', 'Estimated N.2'
           ]

# format values, set data types, and coerce errors
data['Min No. Indivs (Mt+1)'] = pd.to_numeric(data['Min No. Indivs (Mt+1)'], errors='coerce', downcast='integer')
data['No. captures'] = pd.to_numeric(data['No. captures'], errors='coerce', downcast='integer')
data['Sampling Start Date'] = pd.to_datetime(data['Sampling Start Date'], errors='coerce')
data['Sampling End Date'] = pd.to_datetime(data['Sampling End Date'], errors='coerce')
data['StartYear'] = pd.to_datetime(data['StartYear'], errors='coerce', format='%Y')
data['EndYear'] = pd.to_datetime((data['EndYear'].astype(str) + '-12-31'), errors='coerce')
data['Publication Title'] = data['Publication Title'].replace('\n', '', regex=True)
data['Site Name'] = data['Site Name'].replace('\n', '', regex=True)

# Non-Spatial capture recapture
data['Estimated D'] = pd.to_numeric(data['Estimated D'], errors='coerce')
data['SE (D)'] = pd.to_numeric(data['SE (D)'], errors='coerce')
data['Lower CI (D)'] = pd.to_numeric(data['Lower CI (D)'], errors='coerce')
data['Upper CI (D)'] = pd.to_numeric(data['Upper CI (D)'], errors='coerce')
data['Estimated N'] = pd.to_numeric(data['Estimated N'], errors='coerce')

# Maximum Likelihood Spatial Capture-Recapture
data['Estimated D.1'] = pd.to_numeric(data['Estimated D.1'], errors='coerce')
data['SE (D).1'] = pd.to_numeric(data['SE (D).1'], errors='coerce')
data['Lower CI (D).1'] = pd.to_numeric(data['Lower CI (D).1'], errors='coerce')
data['Upper CI (D).1'] = pd.to_numeric(data['Upper CI (D).1'], errors='coerce')
data['Estimated N.1'] = pd.to_numeric(data['Estimated N.1'], errors='coerce')

# Bayesian Spatial Capture-Recapture
data['Estimated D.2'] = pd.to_numeric(data['Estimated D.2'], errors='coerce')
data['SD (D)'] = pd.to_numeric(data['SD (D)'], errors='coerce')
data['Lower HPD (D)'] = pd.to_numeric(data['Lower HPD (D)'], errors='coerce')
data['Upper HPD (D)'] = pd.to_numeric(data['Upper HPD (D)'], errors='coerce')
data['Estimated N.2'] = pd.to_numeric(data['Estimated N.2'], errors='coerce')

# filter records with tiger detections
detection_df = data.loc[(data['Min No. Indivs (Mt+1)'] > 0)
                        | (data['No. captures'] > 0)
                        | (data['Estimated D'] > 0)
                        | (data['Estimated D.1'] > 0)
                        | (data['Estimated D.2'] > 0)]

detection_df = detection_df[columns]

# fill missing dates with study year
detection_df['Sampling Start Date'].fillna(detection_df['StartYear'], inplace=True)
detection_df['Sampling End Date'].fillna(detection_df['EndYear'], inplace=True)
# detection_df['study midpoint'] = (detection_df['Sampling Start Date'] +
#                                  (detection_df['Sampling End Date'] - detection_df['Sampling Start Date']) / 2)

# fill missing contact information
detection_df['Publication Contact (email)'].fillna('harihar.abishek@gmail.com', inplace=True)
detection_df['Publication Contact (Name)'].fillna('Abishek Harihar', inplace=True)
detection_df['organizational affiliation'].fillna('Panthera', inplace=True)

# calculate standard error from CI if standard error is missing
for index, row in detection_df.iterrows():

    # Non-Spatial capture recapture
    if pd.isnull(row['SE (D)']):
        if pd.notnull(row['Estimated D']):
            if pd.notnull(row['Upper CI (D)']):
                detection_df.loc[index, 'SE (D)'] = high_ci_to_se(row['Upper CI (D)'], row['Estimated D'])

            elif pd.notnull(row['Lower CI (D)']):
                detection_df.loc[index, 'SE (D)'] = low_ci_to_se(row['Lower CI (D)'], row['Estimated D'])

    # Maximum Likelihood Spatial Capture-Recapture
    if pd.isnull(row['SE (D).1']):
        if pd.notnull(row['Estimated D.1']):
            if pd.notna(row['Upper CI (D).1']):
                detection_df.loc[index, 'SE (D).1'] = high_ci_to_se(row['Upper CI (D).1'], row['Estimated D.1'])

            elif pd.notnull(row['Lower CI (D).1']):
                detection_df.loc[index, 'SE (D).1'] = low_ci_to_se(row['Lower CI (D).1'], row['Estimated D.1'])

    # Bayesian Spatial Capture-Recapture
    if pd.isnull(row['SD (D)']):
        if pd.notnull(row['Estimated D.2']):
            if pd.notnull(['Upper HPD (D)']):
                detection_df.loc[index, 'SD (D)'] = high_ci_to_se(row['Upper HPD (D)'], row['Estimated D.2'])

            elif pd.notnull(row['Lower HPD (D)']):
                detection_df.loc[index, 'SD (D)'] = low_ci_to_se(row['Lower HPD (D)'], row['Estimated D.2'])

# flag records for review
# no density estimate
detection_df['review flag'] = np.where(pd.isnull(detection_df['Estimated D']) &
                                       pd.isnull(detection_df['Estimated D.1']) &
                                       pd.isnull(detection_df['Estimated D.2']),
                                       '[no density estimate]',
                                       '')

# no uncertainty estimate
detection_df['review flag'] = np.where(pd.isnull(detection_df['SE (D)']) &
                                       pd.isnull(detection_df['SE (D).1']) &
                                       pd.isnull(detection_df['SD (D)']),
                                       (detection_df['review flag'] + '[no uncertainty estimate]'),
                                       detection_df['review flag'])

# abundance estimate but no density estimate
detection_df['review flag'] = np.where((pd.isnull(detection_df['Estimated D']) &
                                        pd.isnull(detection_df['Estimated D.1']) &
                                        pd.isnull(detection_df['Estimated D.2'])) &
                                       (pd.notnull(detection_df['Estimated N']) |
                                        pd.notnull(detection_df['Estimated N.1']) |
                                        pd.notnull(detection_df['Estimated N.2'])),
                                       (detection_df['review flag'] + '[abundance no density estimate]'),
                                       detection_df['review flag'])

# density and uncertainty estimates are equal
detection_df['review flag'] = np.where((detection_df['Estimated D'] == detection_df['SE (D)']) |
                                       (detection_df['Estimated D.1'] == detection_df['SE (D).1']) |
                                       (detection_df['Estimated D.2'] == detection_df['SD (D)']),
                                       (detection_df['review flag'] + '[density = uncertainty]'),
                                       detection_df['review flag'])

if detection_review_save:
    detection_df_csv = os.path.join(DATA_DIR, 'abishek_data_summary',
                                    'TigerDensity_detection_review.csv')
    detection_df.to_csv(detection_df_csv, index=False)


# drop records with no uncertainty estimate
detection_df = detection_df.dropna(subset=['SE (D)', 'SE (D).1', 'SD (D)'], how='all')

# drop records with no density estimates
detection_df = detection_df.dropna(subset=['Estimated D', 'Estimated D.1', 'Estimated D.2'], how='all')

# fill density column prioritizing D.2, then D.1, then D using conversion factor
detection_df['density'] = np.nan
detection_df['standard error'] = np.nan
detection_df['model'] = np.nan

detection_df.fillna({'density': detection_df['Estimated D.2'],
                     'standard error': detection_df['SD (D)'],
                     'model': 'D.2'}, inplace=True)

detection_df.fillna({'density': detection_df['Estimated D.1'],
                     'standard error': detection_df['SE (D).1'],
                     'model': 'D.1'}, inplace=True)

detection_df.fillna({'density': detection_df['Estimated D'] * D_D1_conversion_factor,
                     'standard error': detection_df['SE (D)'] * D_D1_conversion_factor,
                     'model': 'D'}, inplace=True)


# concatenate grid majority and point tables then drop duplicates
grid_majority = grid_majority[grid_majority['majority'] == 1]
grid_cells = pd.concat([grid_majority, grid_contains_point]).drop_duplicates().drop(columns='majority')

# drop cells where zones 2 and 3 overlap zone 1 to prevent double counting
# exception cells with points near border of zone 1 and 2
exceptions = [159669, 158907]
grid_zone_overlap = grid_zone_overlap['id'].tolist()

if exceptions in grid_zone_overlap:
    grid_zone_overlap = grid_zone_overlap.remove(exceptions)

# get list of cells excluding cells in zone overlap list
grid_cells = grid_cells[~grid_cells['gridid'].isin(grid_zone_overlap)]

# left join grid ids to detection data on Record ID
detection_df = detection_df.merge(grid_cells, left_on='Record ID', right_on='RecordID', how='left').drop(
    columns='RecordID')

# for each study: create one record for each cell in the study area
d = []
for i in set(detection_df['Record ID'].tolist()):
    # list of grid cells for record
    grid_id_list = detection_df[detection_df['Record ID'] == i]['gridid'].tolist()
    grid_cell_count = len(grid_id_list)

    #  assign attributes and format for ad hoc template
    country = detection_df[detection_df['Record ID'] == i]['Tiger Range Country'].values[0]
    name_of_observer = detection_df[detection_df['Record ID'] == i]['Publication Contact (Name)'].values[0]
    email_address = detection_df[detection_df['Record ID'] == i]['Publication Contact (email)'].values[0]
    organizational_affiliation = detection_df[detection_df['Record ID'] == i]['organizational affiliation'].values[0]
    site_name = detection_df[detection_df['Record ID'] == i]['Site Name'].values[0]
    year_pub = int(detection_df[detection_df['Record ID'] == i]['Year of publication'].values[0])
    title_pub = detection_df[detection_df['Record ID'] == i]['Publication Title'].values[0]
    start_observation_date = detection_df[detection_df['Record ID'] == i]['Sampling Start Date'].values[0]
    end_observation_date = detection_df[detection_df['Record ID'] == i]['Sampling End Date'].values[0]
    density = detection_df[detection_df['Record ID'] == i]['density'].values[0]
    standard_error = detection_df[detection_df['Record ID'] == i]['standard error'].values[0]
    notes = "{record_id} : {year_pub} : {title_pub} : {site_name}".format(
        record_id=int(i), year_pub=year_pub, title_pub=title_pub, site_name=site_name)

    # for each unique cell id associated with the site append ad hoc data
    for grid_id in set(grid_id_list):
        deployment_id = '{record_id}_{grid_id}'.format(record_id=i, grid_id=grid_id)

        d.append(
                    {
                        'country': country,
                        'grid': 'tiger_zone_grid',
                        'name of observer/PI': name_of_observer,
                        'email address': email_address,
                        'organizational affiliation': organizational_affiliation,
                        'grid cell label': grid_id,
                        'start observation date': start_observation_date,
                        'end observation date': end_observation_date,
                        'Photograph': 1,
                        'density': density,
                        'density standard error': standard_error,
                        'notes': notes,
                    }
                )

ad_hoc = pd.concat([ad_hoc, pd.DataFrame(d)])


if ad_hoc_save:
    ad_hoc_csv = os.path.join(DATA_DIR, 'abishek_data_summary',
                              'tiger_density_compilation_detection_ad_hoc_grid.csv')
    ad_hoc.to_csv(ad_hoc_csv, index=False)

