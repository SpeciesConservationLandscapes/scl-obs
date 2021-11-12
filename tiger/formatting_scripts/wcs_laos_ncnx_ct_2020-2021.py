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

REFERENCE = "Rasphone A. 2021. WCS Laos NCNX Camera Trap Compilation 2020-2021."

# Import data and TIP templates
sheet_1 = pd.read_excel(os.path.join(UNFORMATTED_DIR, "CT_NCNX_WCS_Data Compilation.xlsx",), sheet_name="CT inst-removal_ENG")
sheet_2 = pd.read_excel(os.path.join(UNFORMATTED_DIR, "CT_NCNX_WCS_Data Compilation.xlsx",), sheet_name="CT inst-removal_ENG 1")

data = pd.concat([sheet_1, sheet_2])

ct_deployment = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry CT deployments latlon.csv"), header=0)
ct_observations = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry ad hoc latlon.csv"), header=0)

data.columns = data.columns.str.replace("\n",'')


# convert UTM to lat lon coordinates
data = data[(data["X"] > 100000) & (data["X"] < 999999)]
data = data[(data["Y"] > 0) & (data["Y"] < 10000000)]
data["latitude"], data["longitude"] = utm.to_latlon(data["X"], data["Y"], 48, "N")
data["deployment ID"] = data["Cam_ID"].map(str) + "_" + data["X"].map(str) + data["Y"].map(str)

data = data[data["Camera condition"] == "Normall/Still have bettery"]

# Populate CT deployment template
ct_deployment["deployment ID"] = data["deployment ID"]
ct_deployment["project ID"] = "NCNX" + "2020-11-02-2021-02-21"
ct_deployment["camera latitude"] = data["latitude"]
ct_deployment["camera longitude"] = data["longitude"]
ct_deployment["country"] = "Laos"
ct_deployment["name of observer/PI"] = data["Observers name"]
ct_deployment["organizational affiliation"] = "WCS"
ct_deployment["email address"] = "arasphone@wcs.org"
ct_deployment["reference"] = REFERENCE
ct_deployment["deployment date/time"] = pd.to_datetime((data["Date_set_up"].map(str) + ' ' + data['Timeset up'].map(str)),errors="coerce" )
ct_deployment["pickup date/time"] = pd.to_datetime((data["Date retrieve"].map(str) + ' ' + data['Time retrieve'].map(str)), errors="coerce")
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
                                 "wcs_2020-2021_laos_ncnx_ct_deployments_latlon.csv")
ct_deployment.to_csv(ct_deployment_csv, index=False)