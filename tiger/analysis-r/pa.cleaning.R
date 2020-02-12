########################################
# Site occupancy data
########################################


# rename variables
s.o.original = rename(s.o.original, 
                      num.surveys = X..replicates.surveyed,
                      gridcode = grid.cell.label, 
                      replicate = replicate..)

s.o.original = s.o.original %>% select(-survey.id) # same on every column

#unique id on grid cell & replicate number
s.o.original$id.survey = cumsum(!duplicated(s.o.original[2:4])) 

max(s.o.original$num.surveys) # 98

# get covariates by grid cell  - hii and woody_cover
s.o.subset<- s.o.original %>% select(gridcode) %>% distinct()
so.occupancy <- merge(woody.cover.hii.all, s.o.subset, by = c("gridcode"))
so.occupancy <- so.occupancy %>% select(-gridcode)

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

#find the overlapping observations
onlyOnes = filter(so.filled_a, observation ==1)
onlyZs = filter(so.filled_a, observation == 0)

reps = plyr::match_df( 
  onlyZs,onlyOnes,
  on = c("id.survey","survey"))
# subtract overlapping observations from the expanded set
final.filled = setdiff(so.filled_a,reps)

strip.so = dplyr::select(final.filled,observation,survey,gridcode, id.survey)

y.so = spread(strip.so, survey, observation)

# remove variables grid and id.survey
y.so <- y.so %>% select(-gridcode, -id.survey)

# create new table with only two columns
temp = matrix(0,ncol = 2, nrow = dim(y.so)[1])
temp[,1] = rowSums(ifelse(is.na(y.so)==FALSE,1,0)) # number of times zero or one
temp[,2] = rowSums(ifelse(is.na(y.so)==FALSE & y.so == 1,1,0)) # number of times tiger was seen 

# remove NaNs
# is.complete = which(so.occupancy$hii != "NaN")
# 
# # only use complete cases
# so.occupancy = so.occupancy[is.complete,]

# temp=temp[is.complete,]# only use complete cases

y.so <- temp

area.so =pi*0.04

X.so=cbind(rep(1, nrow(as.matrix(so.occupancy))), so.occupancy) # 3 columns and 381 rows (2 columns are covariates)
