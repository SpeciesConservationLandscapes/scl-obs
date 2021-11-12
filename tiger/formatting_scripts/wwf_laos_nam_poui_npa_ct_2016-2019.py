import pandas as pd
import os
import utm
import datetime
from datetime import date, time

# Paths
PROJECT_DIR = r"C:\Users\jesse\PycharmProjects\scl-obs\tiger"
DATA_DIR = r"C:\Users\jesse\Documents\wcs_tiger\data"
UNFORMATTED_DIR = os.path.join(DATA_DIR, "unformatted_data")
FORMATTED_DIR = os.path.join(DATA_DIR, "tip_formatted_data")
TEMPLATE_DIR = os.path.join(PROJECT_DIR, "ingest_template")

REFERENCE = "WWF. 2019. WWF Laos Nam Poui NPA Camera Trap Compilation 2016-2019. WWF."

DATE_FILTER = datetime.datetime(2014,1,1)

# Import data and TIP templates
data = pd.read_excel(os.path.join(UNFORMATTED_DIR, "Nam_Poui NPA_CT locations 2016-2019.xlsx"), sheet_name="locations")
# prey_list = pd.read_csv(os.path.join(PROJECT_DIR, "prey_list", "2021-07-22_prey_list.csv"), header=0)


ct_deployment = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry CT deployments latlon.csv"), header=0)

# convert UTM to lat lon coordinates
data = data[(data["X"] > 100000) & (data["X"] < 999999)]
data = data[(data["Y"] > 0) & (data["Y"] < 10000000)]
data["latitude"], data["longitude"] = utm.to_latlon(data["X"], data["Y"], 47, "N")


data["deployment ID"] = data["Location ID"].map(str) + "_" + \
                        data["CT ID"] + "_" + \
                        data["X"].map(str) + "_" + \
                        data["Y"].map(str)

# Populate CT deployment template
ct_deployment["project ID"] =  "nam_poui" + "_" + data["Location ID"]
ct_deployment["deployment ID"] = data["deployment ID"]
ct_deployment["camera latitude"] = data["latitude"]
ct_deployment["camera longitude"] = data["longitude"]
ct_deployment["country"] = "Laos"
ct_deployment["name of observer/PI"] = "WWF"
ct_deployment["organizational affiliation"] = "WWF"
ct_deployment["email address"] = "arasphone@wcs.org"
ct_deployment["reference"] = REFERENCE
ct_deployment["deployment date/time"] = pd.to_datetime(data["Start"].map(str), errors="coerce")
ct_deployment["pickup date/time"] = pd.to_datetime(data["End"].map(str), errors="coerce")
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

ct_deployment_csv = os.path.join(FORMATTED_DIR,
                                 "wwf_2016-2019_nam_poui_ct_deployments_latlon.csv")
ct_deployment.to_csv(ct_deployment_csv, index=False)

print(ct_deployment)

