# ***RPKM_HEATER*** #

INSTALL AND SET UP

git clone https://github.com/bioshaolin/rpkm_heater.git
source ~/rpkm_heater_v1/rpkm_heater/setup/setup.sh

NOTE: rpkm_heater is now callable via $rpkm_heater

RECOMMENDED USAGE \
'''bash
rpkm_heater -map -i <input_directory> -o <output_directory> -project <project_prefix> -sort_samples <sort_samples_list> -sort_gen <sort_gen_list> -colors plasma
'''
SPECIFYING SORTED LISTS

The 2 input options for sorted lists allow for a myriad of approaches to assessing and analyzing your data.

i.e. sorting metagenomes by ocean depth allows the user to visualize abundance in a nearer-to-scale interpretation of ecotypes (SRF --> DEEP).
i.e. sorting genomes by lineage allows the user to potentially identify ecotype clustering.
	#NOTE: by including a sorted genome list the user is also capable of quickly identifying possible outliers. In the event the user has
	identified outlier candidates the sorted list may be updated to exclude those genome(s) and rpkm will automatically un-map those recruitments.

################################
Development: E.W. Getz, 2020
Version: v1.1
Source: https://github.com/bioshaolin/rpkm_heater
