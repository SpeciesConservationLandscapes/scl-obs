import pandas as pd
import numpy as np
import os

# Paths
PROJECT_DIR = r"C:\Users\jesse\PycharmProjects\scl-obs\tiger"
DATA_DIR = r"C:\Users\jesse\Documents\wcs_tiger\data"
UNFORMATTED_DIR = os.path.join(DATA_DIR, "unformatted_data")
FORMATTED_DIR = os.path.join(DATA_DIR, "tip_formatted_data")
TEMPLATE_DIR = os.path.join(PROJECT_DIR, "ingest_template")

# Import data and TIP templates
data = pd.read_csv(os.path.join(UNFORMATTED_DIR, "Cardamom Rainforest Landscape Trap Locations.csv"))
ct_deployment = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry CT deployments latlon.csv"), header=0)
ct_observation = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry CT observations.csv"), header=0)

# CT Deployment
# CT deployment template lat lon
# Columns: [country,
#           grid,
#           name of observer/PI,
#           organizational affiliation,
#           email address,
#           project ID,
#           deployment ID,
#           camera longitude,
#           camera latitude,
#           deployment date/time,
#           pickup date/time,
#           bait,
#           quiet period setting,
#           large prey,
#           small prey,
#           livestock,
#           notes]

# Populate CT deployment template
ct_deployment["deployment ID"] =data["Camera-trap ID"] + "_" + data["lat"].round(3).map(str) + "_" + data["long"].round(3).map(str)
ct_deployment["project ID"] = "gray_cardamom_cambodia_2015-2016"
ct_deployment["camera latitude"] = data["lat"]
ct_deployment["camera longitude"] = data["long"]
ct_deployment["country"] = "Cambodia"
ct_deployment["name of observer/PI"] = "Gray, Thomas"
ct_deployment["organizational affiliation"] = "WWF"
ct_deployment["email address"] = "tgray@wwf-tigers.org"
ct_deployment["reference"] = "Personal Communication: Thomas Gray"
ct_deployment["deployment date/time"] = pd.to_datetime(data["Date Set"], errors="coerce")
ct_deployment["pickup date/time"] = pd.to_datetime(data["Date Removed"], errors="coerce")
ct_deployment["trap effort"] = data["Trap Nights"]
ct_deployment["large prey"] = 0
ct_deployment["small prey"] = 0
ct_deployment["livestock"] = 0
ct_deployment["no detections"] = 1

# drop duplicate rows for deployment data frame
ct_deployment.drop_duplicates(subset=["deployment ID",
                                      "deployment date/time",
                                      "camera latitude",
                                      "camera longitude"], inplace=True)

# CT observation template
# Columns ["project ID",
#          "deployment ID",
#          "observation date/time",
#          "# adult males",
#          "# adult females",
#          "# adults sex unknown",
#          "# Subadults (either sex - 1-2 years old)",
#          "# cubs (either sex - 1-12 month old)"],

# save data frames to CSV

# drop duplicates - each row should be an instance of a unique camera id, location, deployment time
# ct_deployment.drop_duplicates(subset=["deployment ID", "deployment date/time"], inplace=True)
# ct_deployment.dropna(subset=["deployment date/time"], inplace=True)

ct_deployment_csv = os.path.join(FORMATTED_DIR,
                                 "gery_cardamom_rainforest_cambodia_2015-2016_ct_deployments_latlon.csv")
ct_deployment.to_csv(ct_deployment_csv, index=False)
