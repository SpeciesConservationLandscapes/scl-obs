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

REFERENCE = "Rasphone A. 2021. WCS Laos ICBF Camera Trap Compilation 2020-2021."

# Import data and TIP templates
data = pd.read_csv(os.path.join(UNFORMATTED_DIR, "CT_ ICBF_WCS_Data Compilation_NK_2020.csv"))

ct_deployment = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry CT deployments latlon.csv"), header=0)
ct_observations = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry ad hoc latlon.csv"), header=0)

# convert UTM to lat lon coordinates
data["latitude"], data["longitude"] = utm.to_latlon(data["X"], data["Y"], 47, "N")
data["Time set"].fillna("00:00:00", inplace=True)
# print(data["Time set"][143])
# print(data["Date"][143])
# data["Date new"] = data['Date'].strftime.replace(to_replace=".", value="-")


# print(data["Date new"])
# Populate CT deployment template
ct_deployment["project ID"] = data["Survey Site"] + "_2020_05_29-2020_08_20"
ct_deployment["deployment ID"] = data["Camera trap ID"].map(str) + data["X"].map(str) + data["Y"].map(str)
ct_deployment["camera latitude"] = data["latitude"]
ct_deployment["camera longitude"] = data["longitude"]
ct_deployment["country"] = "Laos"
ct_deployment["name of observer/PI"] = data["Leader"]
ct_deployment["organizational affiliation"] = "WCS"
ct_deployment["email address"] = "arasphone@wcs.org"
ct_deployment["reference"] = REFERENCE
ct_deployment["deployment date/time"] = data["Date"].map(str) + ' ' + data['Time set'].map(str)
ct_deployment["pickup date/time"] = pd.to_datetime(data["Date retrived?"], errors="coerce")
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
                                 "wcs_2020_laos_namkan_ct_deployments_latlon.csv")
ct_deployment.to_csv(ct_deployment_csv, index=False)