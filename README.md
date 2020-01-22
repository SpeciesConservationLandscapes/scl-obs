# scl-obs
R code for producing probability grids from observations

## Repository Structure

	|-- tiger  
	
	  |-- analysis-r     	   
		|-- gbig_idigbio_extraction.R   # GBIF iDigBio extraction code
		
		RUN IN THIS ORDER
		|-- import.R   			# 1) import csvs and shapefiles
		|-- pa.cleaning.R   		# 2) clean sign survey data
		|-- pb.cleaning.R   		# 3) clean ad hoc data
		|-- ct.cleaning.R   		# 4) clean camera trap data
		|-- functions_modified.R        # 5) functions needed to run analysis.R below
		|-- analysis.R   		# 6) pa,pb,integrated models
		
	  |-- data                      	# shapefiles and csvs provided by tiger team
	  
	  |-- ingest_template			# csv templates from ingestion portal
