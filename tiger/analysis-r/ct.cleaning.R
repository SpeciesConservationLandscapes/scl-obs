########################################
# Camera trap data
########################################

# "num.surveys" "grid" "observation" "replicate" "id.survey" 

# rename variables with Kim's gridcell shapefile
camera.gridcode <- camera.gridcode %>% mutate(camera.latitude = lat, 
                                              camera.longitude = lon)
camera.gridcode <- camera.gridcode %>% select(grid=gridcode,
                                              camera.latitude,
                                              camera.longitude)

# includes grids that had CT but no tiger was observed
ct <- plyr::join(tiger.CT.entry, tiger.CT.observations, by = "deployment.ID", type = "full")

# create a variable for the number of replicates per survey (one a day)
# create new variables
ct <- ct %>% mutate(# number of days between pick up and deployment
  num.surveys = as.Date(as.character(pickup.date.time), 
                        format="%Y/%m/%d")-
    as.Date(as.character(deployment.date.time), 
            format="%Y/%m/%d"),
  # the day that the tiger was observed
  replicate =   as.Date(as.character(pickup.date.time), 
                        format="%Y/%m/%d")-
    as.Date(as.character(observation.date.time), 
            format="%m/%d/%Y"))

# remove camera locations where the camera was lost
ct <- ct %>% filter(pickup.date.time != "NONE")

# add 0s for where a camera wasn't observed (listed as NAs)
ct$observation.date.time <- as.character(ct$observation.date.time)
ct$observation.date.time[is.na(ct$observation.date.time)] <- 0
ct <- ct %>% mutate(observation = ifelse(observation.date.time == 0, 0, 1))

# add 1s for where there was only one survey and no observation (listed as NAs)
ct$replicate <- as.character(ct$replicate)
ct$replicate[is.na(ct$replicate)] <- 0

ct <- ct %>% select(num.surveys, 
                    observation.date.time, 
                    observation, 
                    replicate, 
                    camera.latitude, 
                    camera.longitude)

# replicate and observation.count
# ct.count <- ct %>% group_by(replicate) %>% summarise(observation.count = sum(observation))
# ct.merged <- merge(ct, ct.count, by="replicate") %>% select(-observation.date.time) %>% distinct()

# merge with CT data to see which grid cell the CT are in
# distinct only? too many duplicates
ct.merged <- merge(ct, camera.gridcode, by = c("camera.latitude","camera.longitude")) %>% distinct()
ct.merged <- ct.merged %>% select(num.surveys, grid, observation.date.time, observation, replicate)

#unique id on grid cell & replicate number
ct.merged$id.survey = cumsum(!duplicated(ct.merged[2:4])) 

# drop variables 
ct.merged <- ct.merged %>% select(num.surveys,
                                  grid,
                                  observation.date.time,
                                  observation,
                                  replicate,
                                  id.survey)

max(ct.merged$num.surveys) # 154 days

# Take all the surveys with NO signs
# create new row for each survey that took 
a = ct.merged %>% 
  filter(observation == 0) %>% 
  crossing(survey =(1:154)) %>% #max number of surveys done
  mutate(good.survey = ifelse(survey>num.surveys, NA, 1)) %>% 
  na.omit()
a = dplyr::select(a,-c(good.survey))

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

# create new table with only two columns
temp = matrix(0,ncol = 2, nrow = dim(y.ct)[1])
temp[,1] = rowSums(ifelse(is.na(y.ct)==FALSE,1,0)) # number of times zero or one
temp[,2] = rowSums(ifelse(is.na(y.ct)==FALSE & y.ct == 1,1,0)) # number of times tiger was seen 

# remove NaNs
is.complete = which(so.occupancy$hii != "NaN")

# only use complete cases
so.occupancy = so.occupancy[is.complete,]

# standardize covariates
so.occupancy$elevation <- tr(so.occupancy$elevation)
so.occupancy$hii <- tr(so.occupancy$hii)

# temp=temp[is.complete,]# only use complete cases

y.ct <- temp

area.so =pi*0.04

X.ct=cbind(rep(1, nrow(as.matrix(so.occupancy))), so.occupancy) # 3 columns and 381 rows (2 columns are covariates)
