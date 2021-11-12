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

REFERENCE = "Griffin O. 2021. WCS Cambodia Biodiversity Database Tiger Record Query 1996-2007. Wildlife Conservation Society."

# Import data and TIP templates
data = pd.read_csv(os.path.join(UNFORMATTED_DIR, "21-05_Tiger extract_BioDivDB_WCS Cambodia_OG.csv"))
adhoc = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry ad hoc latlon.csv"), header=0)

data.dropna(subset=["UTM_E", "UTM_N"], inplace = True)
# data.drop(data[data["UTM_N"] < 100000].index, inplace = True)

for index, row in data.iterrows():
        lat, lon = utm.to_latlon(row["UTM_E"], row["UTM_N"], 48, "N")
        data.loc[index, "observation longitude"] = lon
        data.loc[index, "observation latitude"] = lat
print(data.columns)

adhoc_data = data.copy()[data["Survey_Type"] != "Camera Trapping"]
adhoc_data["Survey_Start"] = pd.to_datetime(adhoc_data["Survey_Start"], errors="coerce")
adhoc_data["Survey_End"] = pd.to_datetime(adhoc_data["Survey_End"], errors="coerce")
adhoc_data["Survey_End"].fillna(adhoc_data["Survey_Start"], inplace=True)

adhoc_data.loc[adhoc_data["Wildlife_Obs_Type"] == "Track", "Tracks"] = 1
adhoc_data.loc[adhoc_data["Wildlife_Obs_Type"] == "Feces", "Scat"] = 1
adhoc_data.loc[adhoc_data["Wildlife_Obs_Type"] == "Heard", "Vocalizations Heard"] = 1
adhoc_data.loc[adhoc_data["Wildlife_Obs_Type"] == "Sgin/Scratch", "Scrapes/Scentmarks"] = 1
adhoc_data.loc[adhoc_data["Wildlife_Obs_Type"] == "Interview", "Field team/staff incidental obs"] = 1


adhoc["start observation date"] = adhoc_data["Survey_Start"]
adhoc["end observation date"] = adhoc_data["Survey_End"]
adhoc["observation latitude"] = adhoc_data["observation latitude"]
adhoc["observation longitude"] = adhoc_data["observation longitude"]
adhoc["country"] = "Cambodia"
adhoc["name of observer/PI"] = "Griffin, Oliver"
adhoc["organizational affiliation"] = "WCS"
adhoc["email address"] = "ogriffin@wcs.org"
adhoc["reference"] = REFERENCE
adhoc["Tracks"] = adhoc_data["Tracks"]
adhoc["Scat"] = adhoc_data["Scat"]
adhoc["Vocalizations Heard"] = adhoc_data["Vocalizations Heard"]
adhoc["Scrapes/Scentmarks"] = adhoc_data["Scrapes/Scentmarks"]
adhoc["Field team/staff incidental obs"] = adhoc_data["Field team/staff incidental obs"]

# for index, row in adhoc_data.itterrows:
    # print(row)



adhoc.to_csv(os.path.join(FORMATTED_DIR, "wcs_cambodia_1996-2007_adhoc_latlon.csv"), index=False)
# data.to_csv(os.path.join(UNFORMATTED_DIR,"21-05_Tiger extract_BioDivDB_WCS Cambodia_OG_latlon.csv"))

