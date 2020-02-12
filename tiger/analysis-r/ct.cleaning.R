########################################
# Camera trap data
########################################

#####################
# import
#####################

# BBSNP2015 CT data
# 31 unique deployments
tiger.CT.observations <- read.csv("tiger/data/Tiger_observation_entry_9_CT_observations_BBSNP_V2.csv")
# 68 unique deployments
tiger.CT.entry <- read.csv("tiger/data/Tiger_observation_entry_9_CT_deployments_latlon_BBSNP.csv")

ct.shp <- readOGR(dsn = "tiger/data/prob 2", layer = "Tiger_observation_entry_9_CT_deployments_latlon_BBSNP_celllabels")
ct.shp.df <- as.data.frame(ct.shp)

unzip("tiger/data/camera_latlon_gridcode.zip")
camera.gridcode <- readOGR(dsn = ".", layer = "camera_latlon_gridcode")
camera.gridcode <- as.data.frame(camera.gridcode)

#####################
# clean data
#####################

# rename variables with Kim's gridcell shapefile
# 63 unique lat/lon values
# we need this file to merge with camera trap observations to see which grid cell the camera is in
camera.gridcode <- camera.gridcode %>% mutate(camera.latitude = lat, 
                                              camera.longitude = lon)
camera.gridcode <- camera.gridcode %>% select(gridcode,
                                              camera.latitude,
                                              camera.longitude)
unique(camera.gridcode$gridcode) # 8 unique grid cells
unique(camera.gridcode$camera.longitude) # 63 unique lat/lon values

ct.shp.df <- ct.shp.df %>% mutate(deployment.ID = deployment,
                                  pickup.date.time = pickup.dat,
                                  deplpyment.date.time = deployme_1,
                                  camera.latitude = camera.lat,
                                  camera.longitude = camera.lon) %>% select(-grid)
unique(ct.shp.df$camera.lon) # 68 unique lat/lon values

# remove missing cameras
# 63 obs
ct.shp.df <- ct.shp.df %>% filter(deployment.ID != c("BBS-2015-Loc-36") &
                                    deployment.ID != c("BBS-2015-Loc-37") &
                                    deployment.ID != c("BBS-2015-Loc-11")&
                                    deployment.ID != c("BBS-2015-Loc-12")&
                                    deployment.ID != c("BBS-2015-Loc-41"))
unique(ct.shp.df$camera.lon) # 63 unique lat/lon values

# tiger.CT.observations <- tiger.CT.observations %>% filter(deployment.ID != c("BBS-2015-Loc-36") &
#                                                           deployment.ID != c("BBS-2015-Loc-37") &
#                                                           deployment.ID != c("BBS-2015-Loc-11")&
#                                                           deployment.ID != c("BBS-2015-Loc-12")&
#                                                           deployment.ID != c("BBS-2015-Loc-41"))

# merge dfs to get observation times, pick up, deployment, and gridcode in one df
ct <- left_join(ct.shp.df, tiger.CT.observations, by = "deployment.ID")
# ct <- plyr::join(ct.shp.df, tiger.CT.observations, by = "deployment.ID", type = "full")
unique(ct$camera.lon) # 63 unique lat/lon values
unique(ct$deployment.ID) # 63 unique deployments
unique(ct$gridcode) # 8 unique grid cells
unique(ct$camera.latitude) # 63 unique lat/lon values

# create a variable for the number of replicates per survey (one a day)
# create new variables
# 154 days max

### use julian package?
### julian(Sys.Date(), -2440588) # from a day

ct <- ct %>% mutate(# number of days between pick up and deployment
    num.surveys = as.Date(as.character(pickup.date.time), 
                        format="%Y/%m/%d")-
                  as.Date(as.character(deplpyment.date.time), 
                          format="%Y/%m/%d"),
  # the day that the tiger was observed
    replicate = as.Date(as.character(pickup.date.time), 
                        format="%Y/%m/%d")-
                as.Date(as.character(observation.date.time), 
                        format="%m/%d/%Y"))

# remove camera locations where the camera was lost
# 63 unique deployment IDs, 63 unique lat/lon
ct <- ct %>% filter(pickup.dat != "NONE") # Removes 5
unique(ct$deployment.ID) # 63 unique deployments
unique(ct$gridcode) # 8 unique grid cells
unique(ct$camera.latitude) # 63 unique lat/lon values

# add 0s for where a camera wasn't observed (listed as NAs)
ct$observation.date.time <- as.character(ct$observation.date.time)
ct$observation.date.time[is.na(ct$observation.date.time)] <- 0
ct <- ct %>% mutate(observation = ifelse(observation.date.time == 0, 0, 1))

# add 1s for where there was only one survey and no observation (listed as NAs)
ct$replicate <- as.character(ct$replicate)
ct$replicate[is.na(ct$replicate)] <- 0

ct <- ct %>% select(num.surveys,
                      gridcode,
                      observation.date.time, 
                      observation, 
                      replicate)

######################
# ct.occupancy
######################

ct.subset<- ct %>% select(gridcode) %>% distinct()

ct.occupancy <- merge(woody.cover.hii.all, ct.subset, by = c("gridcode"))

ct.occupancy <- merge(ct.shp.df, ct.occupancy, by = c("gridcode")) %>% distinct()
ct.occupancy <- ct.occupancy %>% select(hii, woody_cover)

# standardize
ct.occupancy <- ct.occupancy %>% mutate(hii = (hii - means[1])/sds[1],
                                        woody_cover = (woody_cover - means[2])/sds[2])

# remove hour minutes
ct$observation.date.time<-as.Date(as.POSIXct(ct$observation.date.time,format='%m/%d/%Y %H:%M'))

#unique id on grid cell & replicate number
ct$id.survey = cumsum(!duplicated(ct[2:4])) 

# create dataframe of covariates per observation
# ct.occupancy <- ct.occupancy %>% select(hii, srtm)

# drop variables 
ct.merged <- ct 

max(ct.merged$num.surveys) # 154 days expanded
ct.merged <- ct.merged %>% select(num.surveys,
                                  grid = gridcode,
                                  observation,
                                  replicate,
                                  id.survey)

# Take all the surveys with NO signs
# create new row for each survey that took 
a <- ct.merged %>% 
  filter(observation == 0) %>% 
  crossing(survey =(1:154)) %>% #max number of surveys done
  mutate(good.survey = ifelse(survey>num.surveys, NA, 1)) %>% 
  na.omit()
a <- dplyr::select(a,-c(good.survey))

# expand the 1's
b = ct.merged %>% 
  filter(observation == 1) %>% 
  select(-observation) %>% 
  crossing(survey =(1:154)) %>% 
  mutate(good.survey = ifelse(survey>num.surveys, NA, 1)) %>%
  na.omit() %>%
  mutate(observation = ifelse(survey!=replicate, 0, 1))

b = dplyr::select(b,-c(good.survey)) 
#View(s.o.original)

# combine the two
so.filled =rbind(a,b)
so.filled_a = 
  dplyr::select(so.filled,-c(replicate)) %>%    
  distinct(survey,
           observation,
           id.survey,
           .keep_all = T)

#find the overlapping observations
onlyOnes = filter(so.filled_a, observation ==1)
onlyZs = filter(so.filled_a, observation == 0)

reps = plyr::match_df( 
  onlyZs,onlyOnes,
  on = c("id.survey","survey"))
# subtract overlapping observations from the expanded set
final.filled = setdiff(so.filled_a,reps)

strip.so = dplyr::select(final.filled,observation,survey,grid, id.survey)

y.ct = spread(strip.so, survey, observation)

# remove variables grid and id.survey
y.ct <- y.ct %>% select(-grid, -id.survey)

# exactly what we did in the so model
# create new table with only two columns
temp = matrix(0,ncol = 2, nrow = dim(y.ct)[1])
temp[,1] = rowSums(ifelse(is.na(y.ct)==FALSE,1,0)) # number of times zero or one
temp[,2] = rowSums(ifelse(is.na(y.ct)==FALSE & y.ct == 1,1,0)) # number of times tiger was seen 

# temp=temp[is.complete,]# only use complete cases

y.so <- temp

area.so =1

X.so=cbind(rep(1, nrow(as.matrix(ct.occupancy))), ct.occupancy) 

# X.so and y.so should have same number of rows
ct.fit=so.model(X.so,y.so)
ct.fit
