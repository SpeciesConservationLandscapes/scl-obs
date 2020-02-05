###########################################################################################################################################
######### Data required for the function ##########################################################
###################################################################################################
## All the data required for this function is stored in a file data.rda
## s.occupancy - raster with background covatiates that effect occupancy
## s.detection - raster with background covariates that effect detection
## pb.occupancy - matrix with covariates that effect occupancy in the locations of detected presences of the opportunistic survey
## pb.detection - matrix with covariates that effect detection in the locations of detected presences of the opportunistic survey
##
## y.so - matrix of detection/non detection of the PA surveys
## so.occupancy - matrix with covariates that effect occupancy in the locations of PA survey sites
## so.detection - matrix with covariates that effect detection in the locations of PA survey sites in each survey
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

ad.hoc <- read.csv("tiger/data/prob 2/Ad Hoc v9 Sumatra 25NOV2019_V2_singleheader_srtm_hii.csv")

# column of ones for observations
ad.hoc=cbind(rep(1, nrow(as.matrix(ad.hoc))), ad.hoc) 

# select variables
# 29 unique grid cells
ad.hoc <- ad.hoc %>% select(gridcode = cell.label, 
                            hii = sumatragridmrgd2_centroids_hii_hii_1,
                            srtm = sumatragridmrgd2_centroids_srtm_srtm_1,
                            observation = "rep(1, nrow(as.matrix(ad.hoc)))")

# average distance to road
# average TRI
# average HII
# average canopy cover (from UMD)
# 1921 unique grid cells
ad.hoc.covariates <- read.csv("tiger/data/200130_Sumatragrid_covariates.csv")

# merge dataframes
# 1921 unique grid cells
ad.hoc.all <- plyr::join(ad.hoc, ad.hoc.covariates, by = "gridcode", type = "full")
# remove NA values
is.complete = which(is.na(ad.hoc.all$hii)==F &
                      is.na(ad.hoc.all$tri)==F &
                    is.na(ad.hoc.all$woody_cover)==F)
ad.hoc.all = ad.hoc.all[is.complete,]

# standardize covariates
means <- apply(ad.hoc.all[,c("hii","woody_cover","tri","distance_to_roads")],2,mean)
sds <- apply(ad.hoc.all[,c("hii","woody_cover","tri","distance_to_roads")],2,sd)

ad.hoc.all <- ad.hoc.all %>% mutate(hii = (hii - means)/sds,
                                    woody_cover = (woody_cover - means)/sds,
                                    tri = (tri - means)/sds,
                                    distance_to_roads = (distance_to_roads - means)/sds)

# sum(ad.hoc.all$hii)
# sum(ad.hoc.all$tri)
# sum(ad.hoc.all$woody_cover)

# 29 unique grid cells
ad.hoc.29 <- merge(ad.hoc, ad.hoc.all, by="gridcode")
ad.hoc.29 <- ad.hoc.29 %>% select(gridcode, 
                          hii = hii.x, 
                          woody_cover, 
                          distance_to_roads, 
                          tri,
                          observation=observation.y)

# standardize covariates?

# 1921 unique grid cells
pb.occupancy <- ad.hoc.all %>% select(hii,woody_cover)
pb.detection <- ad.hoc.all %>% select(tri,distance_to_roads)

# covariates that affect detection
# 1921 unique grid cells
X.back <- ad.hoc.all %>% select(hii,woody_cover)
X.back = cbind(rep(1, nrow(as.matrix(X.back))), X.back)
X.back <- X.back %>% select(observation = "rep(1, nrow(as.matrix(X.back)))",hii, woody_cover)
X.back <- as.matrix(X.back)

# covariates that affect detection
# 1921 unique grid cells
W.back <- ad.hoc.all %>% select(tri,distance_to_roads)
W.back = cbind(rep(1, nrow(as.matrix(W.back))), W.back)
W.back <- W.back %>% select(observation = "rep(1, nrow(as.matrix(W.back)))",tri,distance_to_roads)
W.back <- as.matrix(W.back)

#area in squared km
area.back = 1
s.area=area.back*nrow(tmpX) #study area

# adding column of ones - po locations

ad.hoc.29 = cbind(rep(1, nrow(as.matrix(ad.hoc.29))), ad.hoc.29)

# 29 unique grid cells
X.po <- ad.hoc.29 %>% select(observation = "rep(1, nrow(as.matrix(ad.hoc.29)))", 
                             hii, 
                             woody_cover)
X.po <- as.matrix(X.po)
W.po <- ad.hoc.29 %>% select(observation = "rep(1, nrow(as.matrix(ad.hoc.29)))", 
                             tri, 
                             distance_to_roads)
W.po <- as.matrix(W.po)

pb.fit=pb.ipp(X.po, W.po, X.back, W.back)

#### Original code

#turning rasters into tables - background, adding column of ones
# X.back = cbind(rep(1, ncell(s.occupancy)), values(s.occupancy))
# colnames(X.back)=c("",names(s.occupancy))
# W.back = cbind(rep(1, ncell(s.detection)), values(s.detection))
# colnames(W.back)=c("",names(s.detection))
# remove all NA values
# tmp=X.back[complete.cases(X.back)&complete.cases(W.back),]
# W.back=W.back[complete.cases(X.back)&complete.cases(W.back),]
# X.back=tmp

#area in squared km -----------------------------------
# area.back = rep((xres(s.occupancy)/1000)*(yres(s.occupancy)/1000), nrow(X.back))# each cell
# s.area=area.back*nrow(X.back) #study area
# 
# # adding column of ones - po locations
# X.pb=cbind(rep(1, nrow(as.matrix(pb.occupancy))), pb.occupancy)
# W.pb=cbind(rep(1, nrow(as.matrix(pb.detection))), pb.detection)

