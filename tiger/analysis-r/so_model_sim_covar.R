#############################################
#     SO Model / Presence-Absence Model
# Simulated Covariates on Ragged y.so data
#############################################

#0. Set working Directory
setwd("~/Desktop/SpeciesConservationLandscapes/scl-obs/tiger/analysis_r")
getwd()

#1. Load required packages - from integrated_sdm.Rmd =========================
##Required Packages
library(tidyverse)
requiredPackages = c('raster', #read shapefiles -- transform to RasterStack *
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

# load functions in separate R file
#!!!!! I had to load functions.R separately for this to work *shrug*
source("functions.r")

#2. Load our y.so data- from integrated_sdm.Rmd===================================

########################################
# Import site occupancy data
########################################

# This section expands the dataframe so that there is a row for each time an area is surveyed. For example, if an area is surveyed 5 times, there are 5 rows for it, with the observation==1 on the times where a tiger or tiger signs were seen at the location in question. 

# set working directory
#setwd("/Users/mari/statistical_consulting/scl-obs/tiger/data")
setwd("~/Desktop/SpeciesConservationLandscapes/scl-obs/tiger/data")
# read csv of SO data
#f = file.choose()
#s.o.original = read.csv("Tiger_observation_entry_9_SS_Observations_SUMATRA.csv" )
s.o.original = read.csv("Tiger_observation_entry_9_SS_Observations_SUMATRA.csv")

# rename variables
s.o.original = rename(s.o.original, 
                      num.surveys = X..replicates.surveyed,
                      grid = grid.cell.label, 
                      replicate = replicate..)

s.o.original = s.o.original %>% select(-survey.id) #same on every column

#unique id on grid cel & replicate number
s.o.original$id.survey = cumsum(!duplicated(s.o.original[2:4])) 

##############################################################
## THE IDEA:
##   - create a bunch of new rows, each row with a 0 or 1 for observed not observed
##   -  flip it to wide format
###############################################################

max(s.o.original$num.surveys) #98

# Take all the surveys with NO signs
# create new row for each survey that took 
a = s.o.original %>% 
  filter(observation == 0) %>% 
  crossing(survey =(1:98)) %>% #max number of surveys done
  mutate(good.survey = ifelse(survey>num.surveys, NA, 1)) %>% 
  na.omit()
a = dplyr::select(a,-c(good.survey))

# expand the 1's
b = s.o.original %>% 
  filter(observation == 1) %>% 
  select(-observation) %>% 
  crossing(survey =(1:98)) %>% 
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

###  
#find the overlapping observations
onlyOnes = filter(so.filled_a, observation ==1)
onlyZs = filter(so.filled_a, observation == 0)

reps = plyr::match_df( 
  onlyZs,onlyOnes,
  on = c("id.survey","survey"))
# subtract overlapping observations from the expanded set
final.filled = setdiff(so.filled_a,reps)
#final.filled$survey_id = cumsum(!duplicated(final.filled[2:4]))
strip.so = dplyr::select(final.filled,observation,survey,grid, id.survey)

# This next section will take that dataframe and turn it into a matrix of values. Each row will correspond to a survey.  If the survey happened 24 times, then the corresponding row will have 24 columns - either 0 or 1 - to denote whether a tiger was seen or not. The final dataframe is called *y.so*.
# final site occupancy data
y.so = spread(strip.so,survey,observation)


#3. Our Simulated Covariates - ==========================================
#These covariates were tested on the simulation file using the Koshkina
#y.so, and they ran. They are normally distributed, with values that 
#don't freak out the model. They are the right sizes and structures for
#our Sumatra Tiger model, which is why we created them, instead of using
#the Koshkina simulated covariates

### our pb.occupancy
pb.detection <- as.data.frame(rnorm(n,0,1))
pb.occupancy <- as.data.frame(rnorm(n,0,1))

###replace so.detection with ours :)
set.seed(1234)
alt <- matrix(rnorm(1,0,1), nrow=394, ncol=48)
so.detection =as.data.frame(alt)

### replace with our so.occupancy
set.seed(1234)
cov <- matrix(rnorm(1,0,1), nrow=394, ncol=48)
so.occupancy = as.data.frame(cov)

# 4. Preparing the data - from sup-0005-PBSO-functions.R in Koshkina paper===

#Preparing Presence-Only data ------------------------------------------------
#turning rasters into tables - background, adding column of ones
X.back = cbind(rep(1, ncell(s.occupancy)), values(s.occupancy))
colnames(X.back)=c("",names(s.occupancy))
W.back = cbind(rep(1, ncell(s.detection)), values(s.detection))
colnames(W.back)=c("",names(s.detection))
# remove all NA values
tmp=X.back[complete.cases(X.back)&complete.cases(W.back),]
W.back=W.back[complete.cases(X.back)&complete.cases(W.back),]
X.back=tmp

#area in squared km -----------------------------------
area.back = rep((xres(s.occupancy)/1000)*(yres(s.occupancy)/1000), nrow(X.back))# each cell
s.area=area.back*nrow(X.back) #study area

# adding column of ones - po locations
X.po=cbind(rep(1, nrow(as.matrix(pb.occupancy))), pb.occupancy)
W.po=cbind(rep(1, nrow(as.matrix(pb.detection))), pb.detection)

#Preparing Presence-Absence data ------------------------------------------------

#add a column of ones to the PA covariat
#y.so # matrix of presences and absences (when the species was and wasn't present)
J.so=ncol(y.so)
X.so=cbind(rep(1, nrow(as.matrix(so.occupancy))), so.occupancy)
W.so = array(dim=c(nrow(as.matrix(so.detection)), J.so, 2))
W.so[,,1] = 1
W.so[,,2] = so.detection# if it changes
W.so[,,2]=as.matrix(so.detection[,1:2])# if it changes
#sometimes this (the line below) runs, sometimes it doesnt 
#W.so[,,3] = as.matrix(so.detection[,3:4])# if it changes

#Analising the Data
# 5. Analising the data - from sup-0005-PBSO-functions.R==================

#Analyzing Presence-Only data
y.so2 = y.so %>% select(-grid,-id.survey)#get rid of grid and id.survey columns
so.fit=so.model(X.so,W.so,y.so2)# Analyzing presence-absence data


