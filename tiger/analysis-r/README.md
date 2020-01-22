# scl-obs
R code for producing probability grids from observations.

Only need to run analysis.R 

## Repository Structure

	|-- tiger  
	
	  |-- analysis-r     	   
		|-- gbig_idigbio_extraction.R   # GBIF iDigBio extraction code
		
		|-- import.R   			# import csvs and shapefiles
		|-- pa.cleaning.R   		# clean sign survey data
		|-- pb.cleaning.R   		# clean ad hoc data
		|-- ct.cleaning.R   		# clean camera trap data
		|-- functions_modified.R        # functions needed to run analysis.R below
		|-- analysis.R   		# pa,pb,integrted models
		
	  |-- data                      	# shapefiles and csvs provided by tiger team
	  
	  |-- ingest_template			# csv templates from ingestion portal
