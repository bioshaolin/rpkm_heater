# ***RPKM_HEATER*** #

## INSTALL AND SET UP ##

	git clone https://github.com/bioshaolin/rpkm_heater.git
	
	echo 'alias rpkm_heater="python3 <ADD-YOUR-PATH-TO-DIR-HERE>/rpkm_heater/rpkm_heater.py"' >> .bashrc
	
	cd rpkm_heater
	
	conda env create -f rpkm_heater_dep.yml -n rpkm_heater

*NOTE: rpkm_heater is now callable via $rpkm_heater*

## HELP MENU ##
	rpkm_heater -h

## RECOMMENDED USAGE ##
	conda activate rpkm_heater
	
	rpkm_heater -map -i <input_directory> -o <output_directory> -project <project_prefix> -sort_samples <sort_samples_list> -sort_gen <sort_gen_list> -colors plasma

## INPUT FORMAT ##
	cat sample.bam.stats
	GenomeA	1110000	379477	0
	GenomeB	1120000	350023	0
	GenomeC	1080000	289000	0
*Format is a tab-delimited 4 column (Genome	Genome_length	Reads_mapped	Reads_unmapped) stats file(s).* \
*NOTE: Do not add headers!* \
The inputs for each sample can be generated by running

	samtools idxstats sample.bam > sample.bam.stats
However, any workflow can be used so long as the final format includes the 4 columns (Genome	Genome_length	Reads_mapped	Reads_unmapped) in that order (ext: .stats).
	
## SPECIFYING SORTED/COLOR LISTS ##

*The 3 input options for sorted/color lists offer a myriad of approaches for interpreting your data.*

### Metagenomes/Samples ###
	-sort_format
*Format is tab-delimited list.*
	
	-sort_samples <sorted_samples_list.txt>
Sorting metagenomes by ocean depth or region allows the user to visualize abundance in a nearer-to-scale interpretation of ecotypes (SRF --> DEEP).

### Genomes/Genes ###
	-sort_format
*Format is tab-delimited list.*
	
	-sort_gen <sorted_genome_list.txt>
Sorting genomes/genes by lineage allows the user to potentially identify ecotype clustering. \
	*NOTE: by including a sorted genome list the user is also capable of quickly identifying possible outliers. In the event the user has
	identified outlier candidates the sorted list may be updated to exclude those genome(s) and rpkm_heater will automatically un-map those recruitments.*

### Phylogeny Colors ###
	-phy_col_format
*Format is a tab-delimited 3 column (Genome	Order	Color) txt file.*

	-phylo_colors <lineage_colors.txt>
Providing a color list will highlight the lineage ids respective to your input.
\
\
\
\
\
Development: E.W. Getz, 2020 \
Version: v1.1 \
Source: https://github.com/bioshaolin/rpkm_heater

## WHAT TO EXCPECT IN v2 ##
Version 2 will include:
* a subcommand that combines rpkm_heater outputs for grouped interpretations. This feature will be significant for users who are recruiting with disproportional grouped sample numbers (POS = 105, PON = 50).
* an option to specify which transforation method to call (log2, log10, none).
