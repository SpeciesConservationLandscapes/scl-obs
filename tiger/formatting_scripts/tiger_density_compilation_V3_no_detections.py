import pandas as pd
import numpy as np
import os


def diff(values, target):
    # return the difference list of values and target
    return [target - v for v in values]


def distribute(available, members, strict_equal=False):
    # find across how many 'members' we must distribute 'available'
    # and discover the total sum of those values
    # in order to get diff list for them and the target value
    total = available
    idx = None
    for idx, member in enumerate(members):
        total += member
        if idx >= len(members)-1 \
        or total // (idx+1) <= members[idx+1]:
            break
    count = idx+1
    dist = diff(members[0:count], total // count)
    if not strict_equal:
        for r in range(total % count):
            dist[r] += 1
    return dist

# Paths
PROJECT_DIR = r'C:\Users\jesse\PycharmProjects\scl-obs\tiger'
DATA_DIR = r'C:\Users\jesse\Documents\wcs_tiger\data'
UNFORMATTED_DIR = os.path.join(DATA_DIR, 'unformatted_data')
FORMATTED_DIR = os.path.join(DATA_DIR, 'tip_formatted_data')
TEMPLATE_DIR = os.path.join(PROJECT_DIR, 'ingest_template')

# data = pd.read_excel(os.path.join(UNFORMATTED_DIR, 'TigerDensityCompilation_V_3.2.xlsx'), header=1)
data = pd.read_csv(os.path.join(UNFORMATTED_DIR, 'tiger_density_compilation_V3_ref.csv'), header=0)
ct_deployment = pd.read_csv(os.path.join(TEMPLATE_DIR, 'tiger observation entry CT deployments grid.csv'), header=0)

# Save flags
no_detection_data_save = False
no_detection_check = False
detection_data_save = False
grid_cell_save = False
ct_deployment_save = True

# estimate trap effort flag
estimate_trap_effort = False

# grid_contains_point : all grid cells that contain a point from tiger site center point
# grid_majority : intersection of study area polygon and cell, where tiger site polygon overlaps more than 50% of cell
# grid_zone_overlap : list cells in tiger region grid that overlap
grid_contains_point = pd.read_csv(os.path.join(DATA_DIR, 'harihar_tiger_density',
                                               'TigerDensity_grid_contains_point_2.csv'))

grid_majority = pd.read_csv(os.path.join(DATA_DIR, 'harihar_tiger_density', 'TigerDensity_grid_majority_2.csv'))

grid_zone_overlap = pd.read_csv(os.path.join(DATA_DIR, 'harihar_tiger_density',
                                             'tiger_region_grid_overlap.csv'), header=0)

data_year = pd.read_csv(os.path.join(DATA_DIR, 'harihar_tiger_density',
                                     'TigerDensity_compilation_startyear_endyear.csv'), header=0)

data = data.merge(data_year, left_on='Record ID', right_on='RecordID').drop(columns='RecordID')

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
           'Estimated D',
           'Estimated D.1',
           'Estimated D.2',
           'citation',
           'key']

# format values, set data types, and coerce errors
data['Study ID'] = pd.to_numeric(data['Study ID'], errors='coerce', downcast='integer')
data['Record ID'] = pd.to_numeric(data['Record ID'], errors='coerce', downcast='integer')
data['Min No. Indivs (Mt+1)'] = pd.to_numeric(data['Min No. Indivs (Mt+1)'], errors='coerce', downcast='integer')
data['No. captures'] = pd.to_numeric(data['No. captures'], errors='coerce', downcast='integer')
data['Estimated D'] = pd.to_numeric(data['Estimated D'], errors='coerce')
data['Estimated D.1'] = pd.to_numeric(data['Estimated D.1'], errors='coerce')
data['Estimated D.2'] = pd.to_numeric(data['Estimated D.1'], errors='coerce')
data['Trap effort'] = pd.to_numeric(data['Trap effort'], errors='coerce')
data['Sampling Start Date'] =pd.to_datetime(data['Sampling Start Date'], errors='coerce')
data['Sampling End Date'] = pd.to_datetime(data['Sampling End Date'], errors='coerce')
data['StartYear'] = pd.to_datetime(data['StartYear'], errors='coerce', format='%Y')
data['EndYear'] = pd.to_datetime((data['EndYear'].astype(str) + '-12-31'), errors='coerce')
data['Publication Title'] = data['Publication Title'].replace('\n', '', regex=True)
data['Site Name'] = data['Site Name'].replace('\n', '', regex=True)

# filter no detection: study with 0 reported captures or 0 Min No. Individuals and density is 0 or NULL
no_detection_df = data.loc[((data['Min No. Indivs (Mt+1)'] == 0) | (data['No. captures'] == 0)) &
                           ((data['Estimated D'].isnull()) | (data['Estimated D'] == 0)) &
                           ((data['Estimated D.1'].isnull()) | (data['Estimated D.1'] == 0)) &
                           ((data['Estimated D.2'].isnull()) | (data['Estimated D.2'] == 0))]

# drop records that are missing both sampling dates and trap effort
no_detection_df.dropna(subset=['Trap effort'], inplace=True)

# drop specific records
exclude_records = [627]
no_detection_df = no_detection_df[~no_detection_df['Record ID'].isin(exclude_records)]

# estimate trap effort for records with sampling start/end dates and missing reported trap effort
# trap effort is calculated by multiplying study duration by number of CT deployments
# [365, 368, 369, 370, 371, 372, 375, 376, 377, 378, 392, 422, 621, 780, 996, 1171]
if estimate_trap_effort is True:
    # print(no_detection_df[no_detection_df['Trap effort'].isnull()]['Record ID'].tolist())
    no_detection_df['duration'] = (no_detection_df['Sampling End Date'] -
                                   no_detection_df['Sampling Start Date']) / np.timedelta64(1, 'D')
    no_detection_df['estimated_trap_effort'] = no_detection_df['duration'] * no_detection_df['No. of trap location']
    no_detection_df['Trap effort'].fillna(no_detection_df['estimated_trap_effort'], inplace=True)

# for remaining records use study years where sampling dates are missing
no_detection_df['Sampling Start Date'].fillna(no_detection_df['StartYear'], inplace=True)
no_detection_df['Sampling End Date'].fillna(no_detection_df['EndYear'], inplace=True)

# fill missing contact information
no_detection_df['Publication Contact (email)'].fillna('harihar.abishek@gmail.com', inplace=True)
no_detection_df['Publication Contact (Name)'].fillna('Abishek Harihar', inplace=True)
no_detection_df['organizational affiliation'].fillna('Panthera', inplace=True)

# drop unneeded columns
no_detection_df = no_detection_df[columns]

if no_detection_check:
    no_detection_df.to_csv(os.path.join(DATA_DIR, 'harihar_tiger_density','no_detection_check.csv'))

# mask = no_detection_df[no_detection_df["Sampling Start Date"].isnull() | no_detection_df["Sampling End Date"].isnull()]
# mask.to_csv(os.path.join(DATA_DIR, 'abishek_data_summary', 'TigerDensity_compilation_no_date.csv'))

# concatenate grid majority and point tables then drop duplicates
# grid_majority = grid_majority[grid_majority['majority'] == 1]
grid_cells = pd.concat([grid_majority, grid_contains_point]).drop(columns='majority')
grid_cells.drop_duplicates(inplace=True)

# drop cells where zones overlap to prevent double counting area
# exceptions cells with points near border of zone 1 and 2
exceptions = ['159669_2', '158907_2', '175697_2']

grid_zone_overlap = grid_zone_overlap['id'].tolist()

if len(exceptions) > 0:
    grid_zone_overlap = set(grid_zone_overlap) - set(exceptions)

grid_cells = grid_cells[~grid_cells['id'].isin(grid_zone_overlap)]
grid_cells.rename(columns={'id':'gridid'}, inplace=True)

if grid_cell_save is True:
    grid_cells['flag'] = 1
    grid_cells.to_csv(os.path.join(DATA_DIR, 'abishek_data_summary', 'TigerDensity_gridcells_2.csv'), index=False)

# left join grid ids to absence data on Record ID
no_detection_df = no_detection_df.merge(grid_cells, left_on='Record ID', right_on='RecordID', how='left').drop(columns='RecordID')

if no_detection_data_save is True:
    no_detection_data_path = os.path.join(DATA_DIR, 'abishek_data_summary', 'no_detection_data.csv')
    no_detection_df.to_csv(no_detection_data_path, index=False)

# for each study: create one record for each cell in study area, dividing trap effort equally among cells
d = []
for i in set(no_detection_df['Record ID'].tolist()):
    # list of grid cells for record
    grid_id_list = no_detection_df[no_detection_df['Record ID'] == i]['gridid'].tolist()
    grid_cell_count = len(grid_id_list)
    ct_count = no_detection_df[no_detection_df['Record ID'] == i]['No. of trap location'].values[0].astype(int)
    # ct_per_cell = (ct_count / grid_cell_count).astype(int)
    ct_per_cell = distribute(ct_count, [0 for i in range(grid_cell_count)])
    grid_id_ct = dict(zip(grid_id_list, ct_per_cell))
    # calculate trap effort per camera
    trap_effort = no_detection_df[no_detection_df['Record ID'] == i]['Trap effort'].values[0]
    trap_effort_per_cell = trap_effort / grid_cell_count
    trap_effort_per_ct = trap_effort / ct_count
    print('Record ID: ', i, '________________________')
    print('grid id list: ', grid_id_list)
    print('trap effort: ', trap_effort)
    print('grid cell count: ', grid_cell_count)
    print('ct count: ', ct_count)
    print('ct per cell: ', ct_per_cell)
    print('trap effort per ct: ', trap_effort_per_ct)
    print(grid_id_ct)

    #  assign attributes and format for CT deployment template
    country = no_detection_df[no_detection_df['Record ID'] == i]['Tiger Range Country'].values[0]
    name_of_observer = no_detection_df[no_detection_df['Record ID'] == i]['Publication Contact (Name)'].values[0]
    email_address = no_detection_df[no_detection_df['Record ID'] == i]['Publication Contact (email)'].values[0]
    organizational_affiliation = no_detection_df[no_detection_df['Record ID'] == i]['organizational affiliation'].values[0]
    project_id = no_detection_df[no_detection_df['Record ID'] == i]['Study ID'].values[0]
    site_name = no_detection_df[no_detection_df['Record ID'] == i]['Site Name'].values[0]
    year_pub = int(no_detection_df[no_detection_df['Record ID'] == i]['Year of publication'].values[0])
    title_pub = no_detection_df[no_detection_df['Record ID'] == i]['Publication Title'].values[0]
    deployment_date = no_detection_df[no_detection_df['Record ID'] == i]['Sampling Start Date'].values[0]
    pickup_date = no_detection_df[no_detection_df['Record ID'] == i]['Sampling End Date'].values[0]
    reference = no_detection_df[no_detection_df['Record ID'] == i]['citation'].values[0]
    study_id = int(no_detection_df[no_detection_df['Record ID'] == i]['Study ID'].values[0])
    key = no_detection_df[no_detection_df['Record ID'] == i]['key'].values[0]
    notes = 'zotero key: {} | study ID: {} | record ID: {}'.format(key, study_id, int(i))

    # for each unique cell id associated with the site append CT deployment data
    for grid_id in set(grid_id_ct):
        # for ct_no in range(grid_id_ct[grid_id]):
        #     deployment_id = '{record_id}_{grid_id}_{ct_no}'.format(record_id=i, grid_id=grid_id, ct_no=ct_no)
            deployment_id = '{record_id}_{grid_id}'.format(record_id=i, grid_id=grid_id)

            d.append(
                {
                    'country': country,
                    'grid': 'tiger_region_grid',
                    'name of observer/PI': name_of_observer,
                    'email address': email_address,
                    'organizational affiliation': organizational_affiliation,
                    'project ID': project_id,
                    'deployment ID': deployment_id,
                    'grid cell label': grid_id,
                    'deployment date/time': deployment_date,
                    'pickup date/time': pickup_date,
                    'trap effort': trap_effort_per_cell,
                    'bait': 0,
                    'quiet period setting': 0,
                    'large prey': 0,
                    'small prey': 0,
                    'livestock': 0,
                    'no detections': 1,
                    'reference': reference,
                    'notes': notes

                }
            )
        # for ct_no in range(ct_per_cell):
        #     # create unique deployment ID
        #     deployment_id = '{record_id}_{grid_id}_{ct_no}'.format(record_id=i, grid_id=grid_id, ct_no=ct_no)
        #
        #     # append record to dictionary
        #     d.append(
        #         {
        #             'country': country,
        #             'name of observer/PI': name_of_observer,
        #             'email address': email_address,
        #             'project ID': project_id,
        #             'deployment ID': deployment_id,
        #             'grid cell label': grid_id,
        #             'deployment date/time': deployment_date ,
        #             'pickup date/time': pickup_date,
        #             'notes': notes
        #         }
        #     )

# concat dictionary with record values to CT template df
ct_deployment = pd.concat([ct_deployment, pd.DataFrame(d)])

if ct_deployment_save:
    ct_deployment_csv = os.path.join(DATA_DIR, 'harihar_tiger_density',
                                     'harihar_tiger_density_compilation_no_detection_ct_deployments_grid.csv')
    ct_deployment.to_csv(ct_deployment_csv, index=False)
