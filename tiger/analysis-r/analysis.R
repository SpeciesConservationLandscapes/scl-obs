
########################################
# Import and Clean Data
########################################

# import data and load libraries
source('import.R')

source('functions_modified.R')

# clean presence background data
source('pb.cleaning.R')

# clean presence absence data
source('pa.cleaning.R')

# clean camera trap absence data
source('ct.cleaning.R')

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

pb.fit=pb.ipp(X.pb, X.back)

########################
# Integrated model
########################

integrated.fit=pbso.integrated(X.po, W.po,X.back, W.back,X.so,W.so,y.so)
printList(integrated.fit)
