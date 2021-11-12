import pandas as pd
import os
from datetime import datetime


# Paths
PROJECT_DIR = r"C:\Users\jesse\PycharmProjects\scl-obs\tiger"

prey_list = pd.read_csv(os.path.join(PROJECT_DIR, "prey_list", "prey_list.csv"))

list_to_join = pd.read_csv(r"C:\Users\jesse\Downloads\species_list_wcs_laos.csv")
today = datetime.today().strftime('%Y-%m-%d')

prey_list = pd.concat([prey_list, list_to_join])
prey_list.drop_duplicates(keep="first", inplace=True)

prey_list.to_csv(os.path.join(PROJECT_DIR, "prey_list", f"{today}_prey_list.csv"), index=False)
