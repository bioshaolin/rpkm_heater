# ***RPKM_HEATER*** #

### INSTALL AND SET UP ###

	git clone https://github.com/bioshaolin/rpkm_heater.git
	
	echo alias rpkm_heater='python3 rpkm_heater/rpkm_heater.py' >> .bashrc
	
	conda env create -f rpkm_heater_dep.yml -n rpkm_heater

NOTE: rpkm_heater is now callable via $rpkm_heater

### RECOMMENDED USAGE ###
	conda activate rpkm_heater
	
	rpkm_heater -map -i <input_directory> -o <output_directory> -project <project_prefix> -sort_samples <sort_samples_list> -sort_gen <sort_gen_list> -colors plasma

### SPECIFYING SORTED LISTS ###

*The 3 input options for sorted lists allow for a myriad of approaches to assessing and analyzing your data.*

**-sort_samples** sorting metagenomes by ocean depth or region allows the user to visualize abundance in a nearer-to-scale interpretation of ecotypes (SRF --> DEEP).

**-sort_gen** sorting genomes/genes by lineage allows the user to potentially identify ecotype clustering.
	*NOTE: by including a sorted genome list the user is also capable of quickly identifying possible outliers. In the event the user has
	identified outlier candidates the sorted list may be updated to exclude those genome(s) and rpkm will automatically un-map those recruitments.*

################################
Development: E.W. Getz, 2020
Version: v1.1
Source: https://github.com/bioshaolin/rpkm_heater
