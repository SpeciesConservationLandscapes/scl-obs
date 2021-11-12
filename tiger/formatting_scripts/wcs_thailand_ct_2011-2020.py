import pandas as pd
import numpy as np
import os
import utm
from datetime import date, time

# Paths
PROJECT_DIR = r"C:\Users\jesse\PycharmProjects\scl-obs\tiger"
DATA_DIR = r"C:\Users\jesse\Documents\wcs_tiger\data"
UNFORMATTED_DIR = os.path.join(DATA_DIR, "unformatted_data")
FORMATTED_DIR = os.path.join(DATA_DIR, "tip_formatted_data")
TEMPLATE_DIR = os.path.join(PROJECT_DIR, "ingest_template")

REFERENCE = "Pattanavibool A, Sittibal D. 2020. WCS Thailand Camera Trap Records 2011-2020. Wildlife Conservation Society."

ct_deployment = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry CT deployments latlon.csv"))
ct_observation = pd.read_csv(os.path.join(TEMPLATE_DIR,"tiger observation entry CT observations.csv"))

data_2011 = pd.read_csv(os.path.join(UNFORMATTED_DIR, r"CT_THA\CT_THA_csv\wcs_thailand_ct_2011.csv"))
data_2012 = pd.read_csv(os.path.join(UNFORMATTED_DIR, r"CT_THA\CT_THA_csv\wcs_thailand_ct_2012.csv"))
data_2013 = pd.read_csv(os.path.join(UNFORMATTED_DIR, r"CT_THA\CT_THA_csv\wcs_thailand_ct_2013.csv"))
data_2014 = pd.read_csv(os.path.join(UNFORMATTED_DIR, r"CT_THA\CT_THA_csv\wcs_thailand_ct_2014.csv"))
data_2015 = pd.read_csv(os.path.join(UNFORMATTED_DIR, r"CT_THA\CT_THA_csv\wcs_thailand_ct_2015.csv"))
data_2016 = pd.read_csv(os.path.join(UNFORMATTED_DIR, r"CT_THA\CT_THA_csv\wcs_thailand_ct_2016.csv"))
data_2017 = pd.read_csv(os.path.join(UNFORMATTED_DIR, r"CT_THA\CT_THA_csv\wcs_thailand_ct_2017.csv"))
data_2018 = pd.read_csv(os.path.join(UNFORMATTED_DIR, r"CT_THA\CT_THA_csv\wcs_thailand_ct_2018.csv"))
data_2019 = pd.read_csv(os.path.join(UNFORMATTED_DIR, r"CT_THA\CT_THA_csv\wcs_thailand_ct_2019.csv"))
data_2020 = pd.read_csv(os.path.join(UNFORMATTED_DIR, r"CT_THA\CT_THA_csv\wcs_thailand_ct_2020.csv"))

data = pd.concat([data_2011,
                  data_2012,
                  data_2013,
                  data_2014,
                  data_2015,
                  data_2016,
                  data_2017,
                  data_2018,
                  data_2019,
                  data_2020])
print(data.columns)
# data = data.dropna(subset=["CAM_lat", "CAM_long"], inplace=True)
data = data[(data["CAM_lat"] > 0) & data["CAM_long"] > 0]
data.dropna(subset=["Deploy_dat", "Pickup_dat"], inplace=True)
data["Livestock"] = np.where((data["L_livestoc"] == 1) | (data["S_livestoc"] == 1), 1, 0)

print(data)


ct_deployment["project ID"] = data["Project_ID"]
ct_deployment["deployment ID"] = data["Deploy_ID"]
ct_deployment["camera latitude"] = data["CAM_lat"]
ct_deployment["camera longitude"] = data["CAM_long"]
ct_deployment["country"] = data["Country"]
ct_deployment["name of observer/PI"] = data["Name_of_ob"]
ct_deployment["organizational affiliation"] = data["ORG_AFL"]
ct_deployment["email address"] = "anakp@wcs.org"
ct_deployment["reference"] = REFERENCE
ct_deployment["deployment date/time"] = pd.to_datetime(data["Deploy_dat"], errors="coerce")
ct_deployment["pickup date/time"] = pd.to_datetime(data["Pickup_dat"], errors="coerce")
ct_deployment["large prey"] = data["largeprey"]
ct_deployment["small prey"] = data["smallprey"]
ct_deployment["livestock"] = data["L_livestoc"]

ct_observation["project ID"] = data["Project_ID"]
ct_observation["deployment ID"] = data["Deploy_ID"]
ct_observation["observation date/time"] = data['Deploy_dat']
ct_observation["# adult males"] = data["Adult_F"]
ct_observation["# adult females"] = data["Adult_M"]
ct_observation["# adults sex unknown"] = data["Adult_TG"]
ct_observation["# cubs (either sex - 1-12 month old)"] = data["TG_cub"]
ct_observation["# Subadults (either sex - 1-2 years old)"] = data["Subadult"]

ct_observation = ct_observation[(ct_observation["# adults sex unknown"] > 0) |
                                (ct_observation["# adult males"] > 0) |
                                (ct_observation["# adult females"] > 0) |
                                (ct_observation["# Subadults (either sex - 1-2 years old)"] > 0) |
                                (ct_observation["# cubs (either sex - 1-12 month old)"] > 0)]
# save data frames to CSV
ct_deployment_csv = os.path.join(FORMATTED_DIR,
                                 "wcs_thailand_ct_deployments_2011-2020.csv")
ct_deployment.to_csv(ct_deployment_csv, index=False)

ct_observation_csv = os.path.join(FORMATTED_DIR,
                                 "wcs_thailand_ct_observations_2011-2020.csv")
ct_observation.to_csv(ct_observation_csv, index=False)
