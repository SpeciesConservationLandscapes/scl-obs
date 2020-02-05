########################################
# Camera trap data
########################################

# "num.surveys" "grid" "observation" "replicate" "id.survey" 

# rename variables with Kim's gridcell shapefile
# 63 unique lat/lon values
# we need this file to merge with camera trap observations to see which grid cell the camera is in
camera.gridcode <- camera.gridcode %>% mutate(camera.latitude = lat, 
                                              camera.longitude = lon)
camera.gridcode <- camera.gridcode %>% select(gridcode,
                                              camera.latitude,
                                              camera.longitude)

ct.occupancy <- ct.occupancy %>% mutate(deployment.ID = deployment,
                                        pickup.date.time = pickup.dat,
                                        deplpyment.date.time = deployme_1,
                                        camera.latitude = camera.lat,
                                        camera.longitude = camera.lon) %>% select(-grid)

ct <- plyr::join(ct.occupancy, tiger.CT.observations, by = "deployment.ID", type = "full")
unique(ct$deployment.ID) # 68 unique deployments
unique(ct$gridcode) # 8 unique grid cells
unique(ct$camera.latitude) # 68 unique lat/lon values

# create a variable for the number of replicates per survey (one a day)
# create new variables
# 154 days max
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
# 68 unique deployment IDs, 63 unique lat/lon...HOW?!
# ct <- ct %>% filter(pickup.dat != "NONE") # Removes 5
unique(ct$deployment.ID) # 68 unique deployments
unique(ct$gridcode) # 8 unique grid cells
unique(ct$camera.latitude) # 68 unique lat/lon values

# add 0s for where a camera wasn't observed (listed as NAs)
ct$observation.date.time <- as.character(ct$observation.date.time)
ct$observation.date.time[is.na(ct$observation.date.time)] <- 0
ct <- ct %>% mutate(observation = ifelse(observation.date.time == 0, 0, 1))

# add 1s for where there was only one survey and no observation (listed as NAs)
ct$replicate <- as.character(ct$replicate)
ct$replicate[is.na(ct$replicate)] <- 0

# merge covariates into one dataframe, similar to so.occupancy in the so model
ct.occupancy.hii <- merge(ct.occupancy.hii, camera.gridcode, by = c("camera.latitude","camera.longitude")) %>% distinct()
ct.occupancy.srtm <- merge(ct.occupancy.srtm, camera.gridcode, by = c("camera.latitude","camera.longitude")) %>% distinct()
ct.occupancy <- full_join(ct.occupancy.hii, ct.occupancy.srtm, by = c("gridcode","camera.latitude","camera.longitude"))

ct.occupancy <- full_join(ct, ct.occupancy, by = c("gridcode","camera.latitude","camera.longitude"))

ct <- ct.occupancy %>% select(num.surveys,
                              gridcode,
                              observation.date.time, 
                              observation, 
                              replicate)

# replicate and observation.count
# ct.count <- ct %>% group_by(replicate) %>% summarise(observation.count = sum(observation))
# ct.merged <- merge(ct, ct.count, by="replicate") %>% select(-observation.date.time) %>% distinct()

# remove hour minutes
ct$observation.date.time<-as.Date(as.POSIXct(ct$observation.date.time,format='%m/%d/%Y %H:%M'))

#unique id on grid cell & replicate number
ct$id.survey = cumsum(!duplicated(ct[2:4])) 

# create dataframe of covariates per observation
# ct.occupancy <- ct.occupancy %>% select(hii, srtm)

# drop variables 
ct.merged <- ct 

max(ct.merged$num.surveys) # 154 days expanded

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

strip.so = dplyr::select(final.filled,observation,survey,gridcode, id.survey)

y.ct = spread(strip.so, survey, observation)

# remove variables grid and id.survey
y.ct <- y.ct %>% select(-gridcode, -id.survey)

# exactly what we did in the so model
# create new table with only two columns
temp = matrix(0,ncol = 2, nrow = dim(y.ct)[1])
temp[,1] = rowSums(ifelse(is.na(y.ct)==FALSE,1,0)) # number of times zero or one
temp[,2] = rowSums(ifelse(is.na(y.ct)==FALSE & y.ct == 1,1,0)) # number of times tiger was seen 

# remove NaNs
# is.complete = which(ct.occupancy.hii$hii != "NaN")
# 
# # only use complete cases
# ct.occupancy.hii = ct.occupancy.hii[is.complete,]

# standardize covariates using tr function from functions_modified.R
# ct.occupancy$srtm <- tr(ct.occupancy$srtm)
# ct.occupancy$hii <- tr(ct.occupancy$hii)

# temp=temp[is.complete,]# only use complete cases

# the issue here is that we have 57 rows instead of 63 or 68...
y.ct <- temp

area.so =pi*0.04

X.ct=cbind(rep(1, nrow(as.matrix(ct.occupancy))), ct.occupancy) 
