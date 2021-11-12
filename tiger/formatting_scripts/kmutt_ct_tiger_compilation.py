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
data = pd.read_csv(os.path.join(UNFORMATTED_DIR, "kmutt_ct_tiger_compilation.csv"))
ct_deployment = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry CT deployments latlon.csv"), header=0)
ct_observation = pd.read_csv(os.path.join(TEMPLATE_DIR, "tiger observation entry CT observations.csv"), header=0)

reference = None

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

# drop last row of column sums from data frame
data.drop(data.tail(1).index, inplace=True)

# Populate CT deployment template
ct_deployment["project ID"] = data["Site"] + data["frm yr"].astype(str) + data["provider"]
ct_deployment["deployment ID"] = data["ID"]
ct_deployment["camera latitude"] = data["lat"]
ct_deployment["camera longitude"] = data["long"]
ct_deployment["country"] = "Thailand"
ct_deployment["name of observer/PI"] = data["provider"]
ct_deployment["organizational affiliation"] = "King Mongkut's University of Technology Thonburi"
ct_deployment["email address"] = "ttpisanu@gmail.com"
ct_deployment["reference"] = reference
ct_deployment["deployment date/time"] = pd.to_datetime(data["frm yr"].astype(str) + "-01-01", errors="coerce")
ct_deployment["pickup date/time"] = pd.to_datetime(data["till yr"].astype(str) + "-12-31", errors="coerce")
ct_deployment["trap effort"] = data["effort"]
ct_deployment["large prey"] = 0
ct_deployment["small prey"] = 0
ct_deployment["livestock"] = 0
ct_deployment["no detections"] = np.where((data["Tig"] == 0), 1, 0)

# drop duplicate rows for deployment data frame
ct_deployment.drop_duplicates(subset=["deployment ID",
                                      "deployment date/time",
                                      "camera latitude",
                                      "camera longitude"], inplace=True)

ct_deployment.dropna(subset=["trap effort"], inplace=True)

# CT observation template
# Columns ["project ID",
#          "deployment ID",
#          "observation date/time",
#          "# adult males",
#          "# adult females",
#          "# adults sex unknown",
#          "# Subadults (either sex - 1-2 years old)",
#          "# cubs (either sex - 1-12 month old)"],

ct_observation["project ID"] = data["Site"] + data["frm yr"].astype(str) + data["provider"]
ct_observation["deployment ID"] = data["ID"]
ct_observation["observation date/time"] = pd.to_datetime(data["till yr"].astype(str) + "-12-31")
ct_observation["# adults sex unknown"] = data["Tig"]
ct_observation["# adult males"] = 0
ct_observation["# adult females"] = 0
ct_observation["# Subadults (either sex - 1-2 years old)"] = 0
ct_observation["# cubs (either sex - 1-12 month old)"] = 0


# filter on tiger detections
ct_observation = ct_observation[ct_observation["# adults sex unknown"] == 1]

# save data frames to CSV

# drop duplicates - each row should be an instance of a unique camera id, location, deployment time
# ct_deployment.drop_duplicates(subset=["deployment ID", "deployment date/time"], inplace=True)
# ct_deployment.dropna(subset=["deployment date/time"], inplace=True)

ct_deployment_csv = os.path.join(FORMATTED_DIR,
                                 "kmutt_compilation_ct_deployments_latlon.csv")
ct_deployment.to_csv(ct_deployment_csv, index=False)
#
ct_observation_csv = os.path.join(FORMATTED_DIR,
                                 "kmutt_compilation_ct_observations.csv")
ct_observation.to_csv(ct_observation_csv, index=False)
