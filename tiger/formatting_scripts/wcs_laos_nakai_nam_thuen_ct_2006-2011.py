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

REFERENCE = "Rasphone A. 2011. WCS Laos Nakai Nam Thuen Camera Trap Compilation 2006-2011."

# Import data and TIP templates
data = pd.read_excel(os.path.join(UNFORMATTED_DIR, "CT_Nakai_WCS_Data_Compilation.xlsx"), sheet_name="TOTAL_DATA")
prey_list = pd.read_csv(os.path.join(PROJECT_DIR, "prey_list", "2021-07-22_prey_list.csv"), header=0)


ct_deployment = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry CT deployments latlon.csv"), header=0)
ct_observations = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry ad hoc latlon.csv"), header=0)

# convert UTM to lat lon coordinates
data = data[(data["Lon"] > 100000) & (data["Lon"] < 999999)]
data = data[(data["Lat"] > 0) & (data["Lat"] < 10000000)]
data["latitude"], data["longitude"] = utm.to_latlon(data["Lon"], data["Lat"], 48, "N")
data["deployment ID"] = data["RandomNum"].map(str) + "_" + data["Lon"].map(str) + data["Lat"].map(str)


# data["Date new"] = data["Date"].strftime.replace(to_replace=".", value="-")


# print(data["Date new"])
# Populate CT deployment template
ct_deployment["project ID"] =  "Nakai Nam Thuen" + "_" + data["Site"]
ct_deployment["deployment ID"] = data["deployment ID"]
ct_deployment["camera latitude"] = data["latitude"]
ct_deployment["camera longitude"] = data["longitude"]
ct_deployment["country"] = "Laos"
ct_deployment["name of observer/PI"] = "Rasphone, Akchousanh"
ct_deployment["organizational affiliation"] = "WCS"
ct_deployment["email address"] = "arasphone@wcs.org"
ct_deployment["reference"] = REFERENCE
ct_deployment["deployment date/time"] = pd.to_datetime(data["FirstTrap"], errors="coerce")
ct_deployment["pickup date/time"] = pd.to_datetime(data["LastTrap"], errors="coerce")
ct_deployment["large prey"] = 0
ct_deployment["small prey"] = 0
ct_deployment["livestock"] = 0

# Drop duplicates and no data
ct_deployment.drop_duplicates(subset=["camera latitude",
                                      "camera longitude",
                                      "deployment date/time",
                                      "deployment ID"], inplace=True)

ct_deployment.dropna(subset=["deployment date/time", "pickup date/time"], inplace=True)

# get prey lists
large_prey = prey_list[prey_list["prey type"].eq("large prey")]
small_prey = prey_list[prey_list["prey type"].eq("small prey")]
livestock = prey_list[prey_list["prey type"].isin(["large livestock", "small livestock"])]

for index, row in data.iterrows():

    # prey type flags
    sp = 0
    lp = 0
    ls = 0

    deployment_id = row["deployment ID"]

    # list of unique species observed at camera deployment
    species = data.loc[data["Anim."] > 0]
    species = data[data["deployment ID"].eq(deployment_id)].drop_duplicates(subset=["Object/s"])

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
                                 "wcs_2006-2011_laos_nakai_nam_thuen_ct_deployments_latlon.csv")
ct_deployment.to_csv(ct_deployment_csv, index=False)