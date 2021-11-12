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

REFERENCE = "Rasphone A. 2017. WCS Laos NEPL Camera Trap Compilation 2009-2017."

# Import data and TIP templates
data = pd.read_excel(os.path.join(UNFORMATTED_DIR, "CT_NEPL_WCS_Data Compilation.xlsx"), sheet_name="Tiger_CT-loc_2003-2010")
prey_list = pd.read_csv(os.path.join(PROJECT_DIR, "prey_list", "2021-07-22_prey_list.csv"), header=0)


ct_deployment = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry CT deployments latlon.csv"), header=0)
ct_observations = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry CT observations.csv"), header=0)

# convert UTM to lat lon coordinates
data = data[(data["Lon"] > 100000) & (data["Lon"] < 999999)]
data = data[(data["Lat"] > 0) & (data["Lat"] < 10000000)]
data["latitude"], data["longitude"] = utm.to_latlon(data["Lon"], data["Lat"], 48, "N")


data["deployment ID"] = data["Sampling_site"].map(str) + "_" + data["NoCam"].map(str) + "_" + data["Lon"].map(str) + "_" + data["Lat"].map(str)
data.loc[data['Object/s'] == 'Tiger', "# adults sex unknown" ] = 1


# print(data["Date new"])
# Populate CT deployment template
ct_deployment["project ID"] =  "Nam Et Phou Louey" + "_" + data["Sampling_site"]
ct_deployment["deployment ID"] = data["deployment ID"]
ct_deployment["camera latitude"] = data["latitude"]
ct_deployment["camera longitude"] = data["longitude"]
ct_deployment["country"] = "Laos"
ct_deployment["name of observer/PI"] = "Rasphone, Akchousanh"
ct_deployment["organizational affiliation"] = "WCS"
ct_deployment["email address"] = "arasphone@wcs.org"
ct_deployment["reference"] = REFERENCE
ct_deployment["deployment date/time"] = pd.to_datetime((data["DateSet"].map(str) + " " + data["TimeSet"].map(str)) , errors="coerce")
ct_deployment["pickup date/time"] = pd.to_datetime((data["DateRem"].map(str) + " " + data["TimeRem"].map(str)), errors="coerce")
ct_deployment["large prey"] = 0
ct_deployment["small prey"] = 0
ct_deployment["livestock"] = 0

# Drop duplicates and no data
ct_deployment.drop_duplicates(subset=["camera latitude",
                                      "camera longitude",
                                      "deployment date/time",
                                      "deployment ID"], inplace=True)

ct_deployment.dropna(subset=["deployment date/time", "pickup date/time"], inplace=True)

ct_observations["project ID"] = "Nam Et Phou Louey" + "_" + data["Sampling_site"]
ct_observations["deployment ID"] = data["deployment ID"]
ct_observations["observation date/time"] = pd.to_datetime((data["DateTaken"].map(str) + " " + data["TimeTaken"].map(str)) , errors="coerce")
ct_observations["observation date/time"].fillna(pd.to_datetime((data["DateSet"].map(str) + " " + data["TimeSet"].map(str))), inplace=True)
ct_observations["# adults sex unknown"] = data["# adults sex unknown"].astype("int32")

ct_deployment_csv = os.path.join(FORMATTED_DIR,
                                 "wcs_2003-2010_nam_et_phou_louey_ct_deployments_latlon.csv")
ct_deployment.to_csv(ct_deployment_csv, index=False)

ct_observations_csv = os.path.join(FORMATTED_DIR,
                                 "wcs_2003-2010_nam_et_phou_louey_ct_observations.csv")
ct_observations.to_csv(ct_observations_csv, index=False)
print(ct_deployment)

