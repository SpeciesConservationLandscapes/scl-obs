import pandas as pd
import os
import utm
from datetime import date, time

# Paths
PROJECT_DIR = r"C:\Users\jesse\PycharmProjects\scl-obs\tiger"
DATA_DIR = r"C:\Users\jesse\Documents\wcs_tiger\data"
UNFORMATTED_DIR = os.path.join(DATA_DIR, "unformatted_data")
FORMATTED_DIR = os.path.join(DATA_DIR, "tip_formatted_data")
TEMPLATE_DIR = os.path.join(PROJECT_DIR, "ingest_template")

REFERENCE = "Rasphone A. 2009. WCS Laos Nam Kading Camera Trap Compilation 2007-2009."

# Import data and TIP templates
data_dep = pd.read_excel(os.path.join(UNFORMATTED_DIR, "CT_NKD_WCS_Data Compilation.xlsx"), sheet_name="CT-Table")
data_obs = pd.read_excel(os.path.join(UNFORMATTED_DIR, "CT_NKD_WCS_Data Compilation.xlsx"), sheet_name="FrameInfo")
prey_list = pd.read_csv(os.path.join(PROJECT_DIR, "prey_list", "2021-07-22_prey_list.csv"), header=0)


ct_deployment = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry CT deployments latlon.csv"), header=0)
ct_observations = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry ad hoc latlon.csv"), header=0)

# Flagged Records (error in location reporting)
flag_records = ["A008"]

# Drop flagged records
data_dep = data_dep[~data_dep["Location"].isin(flag_records)]

# convert UTM to lat lon coordinates
data_dep.drop(data_dep.index[(data_dep["Lat"] == 0) | (data_dep["Lon"] == 0) ], inplace=True)
data_dep["latitude"], data_dep["longitude"] = utm.to_latlon(data_dep["Lon"], data_dep["Lat"], 48, "N")

# Populate CT deployment template
ct_deployment["project ID"] = data_dep["Survey_Area"] + "_" + data_dep["Sampling_site"]
ct_deployment["deployment ID"] = data_dep["Location"].map(str) + data_dep["Lon"].map(str) + data_dep["Lat"].map(str)
ct_deployment["camera latitude"] = data_dep["latitude"]
ct_deployment["camera longitude"] = data_dep["longitude"]
ct_deployment["country"] = "Laos"
ct_deployment["name of observer/PI"] = "Rasphone, Akchousanh"
ct_deployment["organizational affiliation"] = "WCS"
ct_deployment["email address"] = "arasphone@wcs.org"
ct_deployment["reference"] = REFERENCE
ct_deployment["deployment date/time"] = pd.to_datetime(data_dep["D/TSet"], errors="coerce")
ct_deployment["pickup date/time"] = pd.to_datetime(data_dep["D/TRem"], errors="coerce")
ct_deployment["large prey"] = 0
ct_deployment["small prey"] = 0
ct_deployment["livestock"] = 0
ct_deployment["no detections"] = 1

# Drop duplicates and no data
ct_deployment.drop_duplicates(subset=["camera latitude",
                                      "camera longitude",
                                      "deployment date/time",
                                      "deployment ID"], inplace=True)

ct_deployment.dropna(subset=["deployment date/time", "pickup date/time"], inplace=True)
data_obs["deployment ID"] = data_dep["Location"].map(str) + data_dep["Lon"].map(str) + data_dep["Lat"].map(str)

# get prey lists
large_prey = prey_list[prey_list["prey type"].eq("large prey")]
small_prey = prey_list[prey_list["prey type"].eq("small prey")]
livestock = prey_list[prey_list["prey type"].isin(["large livestock", "small livestock"])]

for index, row in data_obs.iterrows():

    # prey type flags
    sp = 0
    lp = 0
    ls = 0

    deployment_id = row["deployment ID"]

    # list of unique species observed at camera deployment
    species = data_obs[data_obs["deployment ID"].eq(deployment_id)].drop_duplicates(subset=["Object/s"])

    # if observed species is in prey list set prey values in ct deployment to 1
    for s in species["Object/s"]:

        if s in small_prey["Species"].tolist() and lp == 0:
            sp = 1
        if s in large_prey["Species"].tolist() and lp == 0:
            lp = 1
        if s in livestock["Species"].tolist() and ls == 0:
            ls = 1

    if deployment_id in ct_deployment["deployment ID"].tolist():
        ct_deployment.loc[ct_deployment["deployment ID"] == deployment_id, "large prey"] = lp
        ct_deployment.loc[ct_deployment["deployment ID"] == deployment_id, "small prey"] = sp
        ct_deployment.loc[ct_deployment["deployment ID"] == deployment_id, "livestock"] = ls




ct_deployment_csv = os.path.join(FORMATTED_DIR,
                                 "wcs_2007-2009_laos_nam_kading_ct_deployments_latlon.csv")
ct_deployment.to_csv(ct_deployment_csv, index=False)