
################################
# iDigBio and GBIF Extraction
################################

# install libraries
require(dplyr) # data manipulation
require(spocc) # search multiple databases

# setwd("your file path")

################################
# Extract Occurrence Data
################################

# scientific names to query
spnames = c("Panthera tigris", 
            "Panthera tigris sondaica",
            "Panthera tigris subsp. sondaica",
            "Panthera tigris subsp. sumatrae",
            "Panthera tigris sumatrae")

# specify the sources
sources = c("idigbio", 
            "gbif")

# query multiple APIs at once
occurrences = occ(spnames, # species names specified above
                  from = sources, # sources specified above
                  limit = 1000, # limit our records per species to 1,000 
                  has_coords = T #  only retrieve records with lon/lat coordinates
                  #idigbioopts = list(rq = list(basisofrecord = "preservedspecimen")), # type 
                  #gbifopts = list(basisOfRecord = "Preserved specimen" # type 
                  ) 

# ensures that the names in the output match the names we supplied in our query
occurrences = fixnames(occurrences,
                       how = "query")

################################
# Compile Raw Data
################################

# remove duplicates using occ2df function in spocc
# eliminates much raw information so not very useful
# occdf = occ2df(occurrences)

# generate potential combination of species and source due to occdat object structure
(source_species_comb = expand.grid(sources, gsub(" ","_",spnames)))

# use these combinations to assemble strings that will extract individual data frames
(source_species_string = paste("occurrences",
                               source_species_comb$Var1,
                               "data",
                               source_species_comb$Var2,
                               sep = "$"))

# pull all of the data into one raw data set
raw = eval(parse(text = (paste("bind_rows(",
                               paste(source_species_string,
                                     collapse = ","),
                               ")"))))

# change country names to lowercase
raw$country <- tolower(raw$country)

# keep machine and human observations
tiger_obs <- raw %>% dplyr::filter(basisOfRecord == 'HUMAN_OBSERVATION' |
                            basisOfRecord == 'MACHINE_OBSERVATION',
                            country == 'indonesia'|
                            country == 'india'|
                            country == 'malaysia'|
                            country == 'russia'|
                            country == 'thailand')

# remove columns where all values are NA
tiger_obs <- tiger_obs[,colSums(is.na(tiger_obs))<nrow(tiger_obs)]

################################
# Sign survey data
################################

tiger_SS_raw <- tiger_obs %>% dplyr::filter(basisOfRecord == 'HUMAN_OBSERVATION',
                                            )

tiger_SS <- tiger_SS_raw %>%  dplyr::select(country, 
                                     recordedBy,
                                     institutionCode,
                                     eventDate,
                                     longitude,
                                     latitude,
                                     geodeticDatum,
                                     locality,
                                     informationWithheld,
                                     sex,
                                     occurrenceRemarks) %>% 
                              dplyr::mutate('country' = country,
                                    'grid' = NA,
                                    'name of observer/PI' = recordedBy,
                                    'organizational affliation' = institutionCode,
                                    'email address' = NA,
                                    'observation date' = eventDate,
                                    'grid cell label' = NA, 
                                    'observation longitude' = round(longitude, digits = 5),
                                    'observation latitude' = round(latitude, digits = 5),
                                    'GPS' = geodeticDatum,
                                    'Telemetry Fix' = NA,
                                    'Map and Compass' = NA,
                                    'Dead Reckoning (on map)' = NA,
                                    'Report' = NA,
                                    'other (describe in notes)' = NA,
                                    'location notes' = locality, 
                                    'Patrol Team' = NA, 
                                    'Field team/staff incidental obs' = NA,
                                    'local informant' = NA,
                                    'other'= informationWithheld, 
                                    'Photograph'= NA,
                                    'Firsthand Sighting'= NA,
                                    'Tracks'= NA,
                                    'Scat'= NA,
                                    'Telemetry'= NA,
                                    'Tiger Mortality'= NA,
                                    'Tiger Kill'= NA,
                                    'Vocalizations Heard'= NA,
                                    'Scrapes, Scentmarks'= NA,
                                    'Report'= NA,
                                    'other (describe in notes)' = NA,
                                    'observation notes'= NA,
                                    '# adult males' = ifelse(sex=="MALE",1,0),
                                    '# adult females' = ifelse(sex=="FEMALE",1,0),
                                    '# adults sex unknown' = ifelse(sex == 'NA',1,0),
                                    '# Subadults (either sex - 1-2 years old)' = NA,
                                    '# cubs (either sex - 1-12 month old)' = NA,
                                    'notes' = occurrenceRemarks) 

# remove unwanted columns
tiger_SS <- tiger_SS %>% dplyr::select(-recordedBy,
                             -institutionCode,
                             -eventDate,
                             -longitude,
                             -latitude,
                             -geodeticDatum,
                             -locality,
                             -informationWithheld,
                             -sex,
                             -occurrenceRemarks)

# str(tiger_SS)
# table(tiger_SS$`# adult males`)
# table(tiger_SS$`# adult females`)

# write csv
write_csv(tiger_SS, file = "tiger_SS_iDigBio_GBIF.csv")

################################
# Camera trap data
################################

tiger_CT_raw <- tiger_obs %>% dplyr::filter(basisOfRecord == 'MACHINE_OBSERVATION')

tiger_CT <- tiger_CT_raw %>%  dplyr::select(country, 
                                            recordedBy,
                                            institutionCode,
                                            eventDate,
                                            longitude,
                                            latitude,
                                            geodeticDatum,
                                            locality,
                                            informationWithheld,
                                            sex,
                                            occurrenceRemarks) %>% 
  dplyr::mutate('country' = country,
                'grid' = NA,
                'name of observer/PI' = recordedBy,
                'organizational affliation' = institutionCode,
                'email address' = NA,
                'observation date' = eventDate,
                'grid cell label' = NA, 
                'observation longitude' = round(longitude, digits = 5),
                'observation latitude' = round(latitude, digits = 5),
                'GPS' = geodeticDatum,
                'Telemetry Fix' = NA,
                'Map and Compass' = NA,
                'Dead Reckoning (on map)' = NA,
                'Report' = NA,
                'other (describe in notes)' = NA,
                'location notes' = locality, 
                'Patrol Team' = NA, 
                'Field team/staff incidental obs' = NA,
                'local informant' = NA,
                'other'= informationWithheld, 
                'Photograph'= NA,
                'Firsthand Sighting'= NA,
                'Tracks'= NA,
                'Scat'= NA,
                'Telemetry'= NA,
                'Tiger Mortality'= NA,
                'Tiger Kill'= NA,
                'Vocalizations Heard'= NA,
                'Scrapes, Scentmarks'= NA,
                'Report'= NA,
                'other (describe in notes)' = NA,
                'observation notes'= NA,
                '# adult males' = ifelse(sex=="MALE",1,0),
                '# adult females' = ifelse(sex=="FEMALE",1,0),
                '# adults sex unknown' = ifelse(sex == 'NA',1,0),
                '# Subadults (either sex - 1-2 years old)' = NA,
                '# cubs (either sex - 1-12 month old)' = NA,
                'notes' = occurrenceRemarks) 

# remove unwanted columns
tiger_CT <- tiger_CT %>% dplyr::select(-recordedBy,
                                       -institutionCode,
                                       -eventDate,
                                       -longitude,
                                       -latitude,
                                       -geodeticDatum,
                                       -locality,
                                       -informationWithheld,
                                       -sex,
                                       -occurrenceRemarks)

#str(tiger_CT)

# write csv
write_csv(tiger_CT, file = "tiger_CT_iDigBio_GBIF.csv")