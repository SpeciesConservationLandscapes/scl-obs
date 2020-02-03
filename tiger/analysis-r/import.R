########################################
# Load packages or install packages if they don't exist
########################################

requiredPackages = c('raster',
                     'fields',
                     'mvtnorm',
                     'matrixStats', # matrix functions
                     'readr', # read files
                     'rgdal', 
                     'ggplot2', # visualization
                     'dplyr', # data manipularion
                     'tidyverse',
                     'rgbif', # import ad hoc data from GBIF
                     'tidyr' # data tidying
) 
for(p in requiredPackages){
  if(!require(p,character.only = TRUE)) install.packages(p)
  library(p,character.only = TRUE)
}

# source("tiger/analysis-r/functions_modified.R") # read functions

########################################
# Import data
########################################

###
# 1 Site Occupancy
###

# 394 unique grid cells
s.o.original = read.csv("tiger/data/Tiger_observation_entry_9_SS_Observations_SUMATRA.csv")

so.occupancy <- read.csv("tiger/data/prob/Tiger_observation_entry_9_SS_Observations_SUMATRA_srtm_hii.csv")

###
# 2 Camera Trap
###

# BBSNP2015 CT data
# 8 unique grid cells
tiger.CT.observations <- read.csv("tiger/data/Tiger_observation_entry_9_CT_observations_BBSNP_V2.csv")
tiger.CT.entry <- read.csv("tiger/data/Tiger_observation_entry_9_CT_deployments_latlon_BBSNP.csv")

# Leuser data doesn't have observation date
tiger.CT.observations2 <- read.csv("tiger/data/Tiger_observation_entry_9_CT_deployments_latlon_Leuser_V2.csv")
# tiger.CT.entry2 <- read.csv("tiger/data/Tiger_observation_entry_9_CT_deployments_observations_Leuser_V2.csv")

###
# 3 Ad Hoc
###

# 29 unique grid cells
pb.original <- read.csv("tiger/data/Ad Hoc v9 Sumatra 25NOV2019_V2.csv", skip = 1)

########################################
# Sumatran Grid Cells
########################################

# import Sumatra shapefile of gridcells 
unzip("tiger/data/sumatragridmrgd.zip")
sumatra.map <- readOGR(dsn = ".", layer = "sumatragridmrgd")

# import shapefile of camera lat long and corresponding grid cells
# only includes grid cells for Puspurini data, not Leuser - 8 unique grid cells
unzip("tiger/data/camera_latlon_gridcode.zip")
camera.gridcode <- readOGR(dsn = ".", layer = "camera_latlon_gridcode")
camera.gridcode <- as.data.frame(camera.gridcode)

########################################
# Shapefiles of Covariates
########################################

# prob.zip provided by Kim Fischer

# # create list of all .shp files in folder (case of "shp" matters)
filenames <- list.files(path="tiger/data/prob", pattern=".*shp")

# read in each shp file
for (i in 1:length(filenames)){
  assign(filenames[i], rgdal::readOGR(paste("tiger/data/prob/", filenames[i], sep=''))
         # figure out how to raster in this loop?
  )}

# convert to raster layer
ct.hii <- raster(Tiger_observation_entry_9_CT_deployments_latlon_BBSNP_hii.shp)
ct.srtm<-raster(Tiger_observation_entry_9_CT_deployments_latlon_BBSNP_srtm.shp)
ct.hii.Leuser<-raster(Tiger_observation_entry_9_CT_deployments_latlon_Leuser_V2_hii.shp)
ct.srtm.Leuser<-raster(Tiger_observation_entry_9_CT_deployments_latlon_Leuser_V2_srtm.shp)

# we need one covariate value per grid point? 
WibiPuspa_1000pts_hii.shp<-raster(WibiPuspa_1000pts_hii.shp)
WibiPuspa_1000pts_srtm.shp<-raster(WibiPuspa_1000pts_srtm.shp)

########################################
## s.occupancy - raster with background covatiates that effect occupancy
## s.detection - raster with background covariates that effect detection
########################################

# standarize using scale?
# s.occupancy <- stack(scale(hii_crop, center=TRUE, scale=TRUE))
# s.detection <- stack(scale(hii_crop, center=TRUE, scale=TRUE))

# ad hoc
s.occupancy <- read.csv("tiger/data/prob/Ad Hoc v9 Sumatra 25NOV2019_V2_singleheader_srtm_hii.csv")

s.occupancy <- s.occupancy %>% select(cell.label, 
                                      elevation = sumatragridmrgd2_centroids_srtm_srtm_1,
                                      hii = sumatragridmrgd2_centroids_hii_hii_1) %>% 
               distinct(cell.label, .keep_all = TRUE) 

########################################
## so.occupancy - matrix with covariates that effect occupancy in the locations of pa survey sites
## so.detection - matrix with covariates that effect detection in the locations of pa survey sites in each survey
########################################

# site occupancy
so.occupancy <- so.occupancy %>% select(grid.cell.label, 
                                        elevation = sumatragridmrgd2_centroids_srtm_srtm_1,
                                        hii = sumatragridmrgd2_centroids_hii_hii_1) %>% 
  distinct(grid.cell.label, .keep_all = TRUE) %>% select(-grid.cell.label)

# camera trap
ct.occupancy.hii <- readOGR(dsn = "tiger/data/prob/", layer = "Tiger_observation_entry_9_CT_deployments_latlon_BBSNP_hii")
ct.occupancy.hii <- as.data.frame(ct.occupancy.hii)
ct.occupancy.hii <- ct.occupancy.hii %>% select(camera.latitude=camera.lat,
                                                  camera.longitude=camera.lon,
                                                  hii = hii_1)

ct.occupancy.srtm <- readOGR(dsn = "tiger/data/prob/", layer = "Tiger_observation_entry_9_CT_deployments_latlon_BBSNP_srtm")
ct.occupancy.srtm <- as.data.frame(ct.occupancy.srtm)
ct.occupancy.srtm <- ct.occupancy.srtm %>% select(camera.latitude=camera.lat,
                                                camera.longitude=camera.lon,
                                                srtm = srtm_1)

