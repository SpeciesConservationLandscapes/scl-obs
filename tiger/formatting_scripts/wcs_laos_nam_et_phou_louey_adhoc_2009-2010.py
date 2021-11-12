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
data = pd.read_excel(os.path.join(UNFORMATTED_DIR, "CT_NEPL_WCS_Data Compilation.xlsx"), sheet_name="TG-Tracks-2009-2010")
prey_list = pd.read_csv(os.path.join(PROJECT_DIR, "prey_list", "2021-07-22_prey_list.csv"), header=0)


adhoc= pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry ad hoc latlon.csv"), header=0)

# convert UTM to lat lon coordinates
data = data[(data["X"] > 100000) & (data["X"] < 999999)]
data = data[(data["Y"] > 0) & (data["Y"] < 10000000)]
data["latitude"], data["longitude"] = utm.to_latlon(data["X"], data["Y"], 48, "N")
data.dropna(subset=["Date"], inplace=True)

adhoc["start observation date"] = pd.to_datetime(data["Date"], errors="coerce")
adhoc["end observation date"] = pd.to_datetime(data["Date"], errors="coerce")
adhoc["observation latitude"] = data["latitude"]
adhoc["observation longitude"] = data["longitude"]
adhoc["country"] = "Laos"
adhoc["name of observer/PI"] = "Rasphone, Akchousanh"
adhoc["organizational affiliation"] = "WCS"
adhoc["email address"] = "arasphone@wcs.org"
adhoc["reference"] = REFERENCE
adhoc["Tracks"] = 1

adhoc_csv = os.path.join(FORMATTED_DIR,
                                 "wcs_2009-2010_nam_et_phou_louey_adhoc_latlon.csv")
adhoc.to_csv(adhoc_csv, index=False)

