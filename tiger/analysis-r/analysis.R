
########################################
# Import and Clean Data
########################################

# import data and load libraries
source('import.R')

# clean presence background data
source('pb.cleaning.R')

# clean presence absence data
source('pa.cleaning.R')

########################################
# Analysis
########################################

########################
# Presence absence model
########################

pa.fit=so.model(X.so,y.so)

########################
# Presence background model
########################

pb.fit=pb.ipp(X.po, W.po, X.back, W.back)

########################
# Integrated model
########################

integrated.fit=pbso.integrated(X.po, W.po,X.back, W.back,X.so,W.so,y.so)
printList(integrated.fit)
