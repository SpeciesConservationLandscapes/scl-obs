########################################
## pb.occupancy - matrix with covariates that effect occupancy in the locations of 
### detected presences of the opportunistic survey
## pb.detection - matrix with covariates that effect detection in the locations of 
### detected presences of the opportunistic survey
########################################

pb <- pb.original %>% select(grid = cell.label, 
                             observation.date,
                             observation = Report)

pb.occupancy = s.occupancy

# pb.occupancy=extract(s.occupancy,pb.loc)
# pb.detection=extract(s.detection,pb.loc)
# 
# is.complete.pb=complete.cases(pb.detection)&complete.cases(pb.occupancy)
# pb.detection=pb.detection[is.complete.pb,]
# pb.occupancy=pb.occupancy[is.complete.pb,]

# print("allocating background")
#turning rasters into tables - background, adding column of ones
X.back = cbind(rep(1, ncell(s.occupancy)), s.occupancy)
# W.back = cbind(rep(1, ncell(s.detection)), values(s.detection))

# remove all NA values
# tmp=X.back[complete.cases(X.back)&complete.cases(W.back),]
# W.back=W.back[complete.cases(X.back)&complete.cases(W.back),]
# X.back=tmp

#area in squared km -----------------------------------
area.back = rep((s.occupancy/1000)*(s.occupancy/1000), nrow(X.back))# each cell
s.area=area.back*nrow(X.back) #study area # error????

# adding column of ones - po locations
X.pb=cbind(rep(1, nrow(as.matrix(pb.occupancy))), pb.occupancy)
