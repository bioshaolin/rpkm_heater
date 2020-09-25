import os
import sys
import argparse
import subprocess
import shutil
import re
import glob
import shlex
import operator
from collections import defaultdict
import time
import pandas as pd
import numpy as np
from pathlib import Path
import textwrap
from sklearn import preprocessing
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import ListedColormap, LinearSegmentedColormap, Normalize
import matplotlib.patches as patches
from mpl_toolkits.axes_grid1 import make_axes_locatable

parser = argparse.ArgumentParser(prog='rpkm_heater',\
formatter_class=argparse.RawDescriptionHelpFormatter,\
description='''####################################################################\n\
## Generate heatmap for RPKM visualization from samtools idxstats ##\n \
\n \
                                ~RPKM~ \n \
                     bacter-a 1 0 2 1 0\n \
                     bacter-b 2 1 1 1 0\n \
                     bacter-c 1 2 0 0 0\n \
                     bacter-d 0 0 4 1 5\n \
                     bacter-e 1 3 1 1 0\n \
                              A B C D E\n \


                            numReads_gen
RPKM =                 ---------------------
              (gen_length/1.0E3)(tot_Reads_sample/1.0E6)

''',\
epilog = textwrap.dedent('''\
################################
Development: E.W. Getz, 2020
Version: v1.1
Source: https://github.com/bioshaolin/rpkm_heater
'''))
subcommands = parser.add_argument_group('## sub-commands, NOTE: CHOOSE 1')
inputs = parser.add_argument_group('## input arguments')
outputs = parser.add_argument_group('## output arguments')
heatmap = parser.add_argument_group('## heatmap arguments')
optional = parser.add_argument_group('## optional arguments')
parser.add_argument('-read', '--read', help="Show Read.me", action="store_true")
parser.add_argument('-dep', '--dependencies', help="List the program dependencies for endopep_peaks", action="store_true")
parser.add_argument('-sort_format', '--sort_format', help="Print a formatting example of sorted_format options", action="store_true")
parser.add_argument('-phy_col_format', '--phy_col_format', help="Print a formatting example of phylo_colors option", action='store_true')
subcommands.add_argument('-count', '--count' ,help="only run count", action="store_true")
subcommands.add_argument('-map', '--map', help="count and heatmap", action="store_true")
inputs.add_argument('-i', help="Specify input directory (idxstats) (_suffix = .stats)")
outputs.add_argument('-o', help="Specify output directory (will be created if no path) (see --clear_all)")
outputs.add_argument('-project', help="name of rpkm project")
heatmap.add_argument('-sort_samples', help="input sorted list for samples")
heatmap.add_argument('-sort_gen', help="input sorted list for genes/genomes")
heatmap.add_argument('-colors', help="specify color gradient (plasma/viridis/blue/red/green) (default:plasma)")
heatmap.add_argument('-phylo_colors', help="input color list for clades/sub-clades")
heatmap.add_argument('-xticks', help="control xticks (on/off) (default:on)")
heatmap.add_argument('-yticks', help="control yticks (on/off) (default:on)")
optional.add_argument('-clear', '--clear_all', help="clear previous output directory specification and data products (use if double-backing out_dir)", action="store_true")
parser._optionals.title="## help arguments"
args = parser.parse_args()

####################
# renavigate to -h #
####################

if len(sys.argv[1:]) == 0:
	parser.print_help()
	parser.exit()
else:
    pass

if args.sort_format:
	print(textwrap.dedent('''\
    # Sorted_list should contain one line of sample prefixes by tab "\t" #

    # i.e. ANE_004_05M.bam.stats, ANE_150_40M.bam.stats -->

             -->   ANE_004_05M \t ANE_150_40M

Full_example:
ANE_004_05M	ANE_150_05M	ANE_151_05M	ANE_152_05M	ANW_141_05M	ANW_142_05M	ANW_145_05M	ANW_146_05M	ANW_148_05M	ANW_149_05M	ASE_66_05M	ASE_67_05M	ASE_68_05M	ASE_70_05M	ASW_72_05M	ASW_76_05M	ASW_78_05M	ASW_82_05M	ION_36_05M	ION_38_05M	ION_41_05M	ION_42_05M	ION_45_05M	ION_48_05M	IOS_52_05M	IOS_56_05M	IOS_57_05M	IOS_62_05M	IOS_64_05M	IOS_65_05M	MED_18_05M	MED_23_05M	MED_25_05M	MED_30_05M	PON_132_05M	PON_133_05M	PON_137_05M	PON_138_05M	PON_140_05M	PSE_100_05M	PSE_102_05M	PSE_109_05M	PSE_110_05M	PSE_111_05M	PSE_93_05M	PSE_94_05M	PSE_96_05M	PSE_98_05M	PSE_99_05M	PSW_112_05M	PSW_122_05M	PSW_123_05M	PSW_124_05M	PSW_125_05M	PSW_128_05M	RED_31_05M	RED_32_05M	RED_33_05M	RED_34_05M	SOC_84_05M	SOC_85_05M	ION_36_17M	ION_38_25M	ION_39_25M	ASE_66_30M	IOS_65_30M	PSE_109_30M	PSE_93_35M	ANE_004_40M	ANE_150_40M	ASW_82_40M	PON_137_40M	PSE_102_40M	PSW_128_40M	PON_133_45M	ASE_68_50M	MED_25_50M	PSE_100_50M	PSE_110_50M	ION_41_60M	MED_18_60M	PON_138_60M	RED_34_60M	IOS_64_65M	IOS_58_66M	MED_30_70M	IOS_52_75M	ANE_151_80M	ION_42_80M	RED_32_80M	PSE_111_90M	SOC_85_90M	ASW_72_100M
'''))
	exit()
else:
	pass

if args.phy_col_format:
	print(textwrap.dedent('''\
	# phylo_colors should contain 3 columns "\t" #
    1. Genome
    2. Order (index starts at 0)
    3. Color (CAn be hexidecimal or standard)

    # i.e. 2503754001	1	#990000

Snippet_example:
2503754001	0	#990000
2706794856	1	blue
2236347020	2	green
    '''))
	exit()
else:
	pass

if args.read:
	subprocess.call("cat ~/rpkm_heater/Read.ME", shell=True)
	exit()
else:
	pass

input_folder = args.i
project_name = args.project
path=args.i
allFiles = glob.glob(path + "/*.stats")

if args.clear_all:
	subprocess.call("rm -rf "+args.o+"; mkdir "+args.o, shell=True)
	subprocess.call("chmod 777 "+args.o, shell=True)
else:
	subprocess.call("mkdir "+args.o, shell=True)
	subprocess.call("chmod 777 "+args.o, shell=True)

#Appending *.stats to df#
list = []
#Appending metG sample name for use throughout pipes#
sample_list = []
#Appending ACC#
acc_list = []
#Appending _totreads to intermediates#
counts_list = []



if args.count:
	for file_ in allFiles:
		samples = os.path.basename(file_)
		samples_1 = os.path.splitext(samples)[0]
		samples_2 = os.path.splitext(samples_1)[0]
		sample_list.append(samples_2)
		df = pd.read_csv(file_, index_col=None, dtype=str, header=None, sep="\t").assign(filename=samples_2)
		df.columns = ['ACC','genome_length','reads_mapped','reads_unmapped','sample']
		df1 = df[['ACC','genome_length','reads_mapped','sample']]
		df1.set_index('ACC', inplace=True)

		gen_length_key = df1[['genome_length']]
		gen_length_key.to_csv('temp1.csv', sep="\t")

		df2 = df1[['reads_mapped','sample']]

		print(df2)
		list.append(df2)
	frame2 = pd.concat(list, axis=1, ignore_index=True)
	print(frame2)
	frame2.to_csv(args.o+"/"+project_name+'_frame2.csv', sep="\t")
	gen_length_key = pd.read_csv("temp1.csv", sep="\t")
	gen_length_key.columns = ['ACC','genome_length']
	gen_length_key.set_index('ACC', inplace=True)
	acc_list.append(gen_length_key.index.values)
	frame3 = pd.concat([gen_length_key,frame2], axis=1, join_axes=[gen_length_key.index])
	print(frame3)
#	frame3.to_csv(args.o+"/"+project_name+'_frame3.csv', sep="\t")

	frame4 = frame3.iloc[0:,1::2]
	print(frame4)
#	frame4.to_csv(args.o+"/"+project_name+'_frame4.csv', sep="\t")
	gen_length_key = pd.read_csv("temp1.csv", sep="\t")
	gen_length_key.columns = ['ACC','genome_length']
	gen_length_key.set_index('ACC', inplace=True)

	counts = pd.concat([gen_length_key,frame4], axis=1, join_axes=[gen_length_key.index])
	print(counts)
	subprocess.call("rm -f temp1.csv", shell=True)

	print(sample_list)
	counts.columns = counts.columns[:1].tolist() + sample_list
	print(counts)

	counts.drop(counts.tail(1).index,inplace=True)
	counts.to_csv(args.o+"/"+project_name+'_counts.csv', sep="\t")

	counts = counts.convert_objects(convert_numeric=True)
	counts.loc['Total',:] = counts.sum(axis=0) / 1000000
	print(counts)
	print(counts.dtypes)

	counts['genome_length']['Total'] = 0
	counts_list.append(counts.loc['Total'])
	counts['genome_length'] = counts['genome_length'] / 1000
	counts = counts.add_suffix('_reads')
	counts=counts.rename(columns = {'genome_length_reads':'genome_length'})
	print(counts)
	print(counts_list)

	df_test = pd.DataFrame(counts_list)
	df_test.drop('genome_length', axis=1, inplace=True)
	df_test = df_test.add_suffix('_totreads')
	print(df_test)

	try1 = pd.concat([df_test,counts], axis=1, join_axes=[counts.index])
	try1=  try1.sort_values(by=['genome_length'], ascending=[True])

	stacker = try1.stack()
	try1 = stacker.unstack()
	try1 = try1.reindex(sorted(try1.columns), axis=1)
	first_col = try1.pop('genome_length')
	try1.insert(0, 'genome_length', first_col)
	try1.fillna(method='ffill', inplace=True)
	try1 = try1.iloc[1:]
	print(try1)

	# RPKM, top = numReads#
	df_top = try1.iloc[0:,1::2]

	# RPKM, bottom = (gen_l/100)(totReads/1000000)#
	df_bottom = try1.iloc[0:,0::2]
	#print(df_top)
	#print(df_bottom)
	df_bottom.memory_usage(deep=True)

	#RPKM, bottom --> gl*tR#
	#print(df_bottom.iloc[0:,1::1])
	df_bottom_2 = df_bottom.iloc[0:,1::1].multiply(df_bottom["genome_length"], axis="index")
	#print(df_bottom_2)


	#RPKM, top/bottom#
	#print(df_top.iloc[0:,0::1])
	df_rpkm = df_top.iloc[0:,0::1].divide(df_bottom_2.values, axis="index")
	df_rpkm.columns = df_rpkm.columns.str.replace('_reads', '', regex=True)
	print(df_rpkm)

	#df_rpkm.to_csv(project_name+"_rpkm.csv", sep="\t")

	#print(acc_list)

	if args.sort_samples and args.sort_gen:
		sorted = pd.read_csv(args.sort_samples, sep="\t")
		print(sorted)
		sorted_list = sorted.columns.tolist()
		print(sorted_list)

		df_rpkm = df_rpkm[sorted_list]

		sorted_y = pd.read_csv(args.sort_gen, sep="\t")
		print(sorted_y)
		sorted_list_y = sorted_y.columns.tolist()
		print(sorted_list_y)

		df_rpkm = df_rpkm.reindex(sorted_list_y)
		df_rpkm = df_rpkm.T
		print(df_rpkm)
		df_rpkm.to_csv(args.o+"/"+project_name+"_rpkm.csv", sep="\t")

	elif args.sort_samples:
		sorted = pd.read_csv(args.sort_samples, sep="\t")
		print(sorted)
		sorted_list = sorted.columns.tolist()
		print(sorted_list)

		df_rpkm = df_rpkm[sorted_list]
		print(df_rpkm)
		df_rpkm.to_csv(args.o+"/"+project_name+"_rpkm.csv", sep="\t")

	elif args.sort_gen:
		sorted = pd.read_csv(args.sort_samples, sep="\t")
		print(sorted)
		sorted_list = sorted.columns.tolist()
		print(sorted_list)

		df_rpkm = df_rpkm[sorted_list]
		print(df_rpkm)
		df_rpkm.to_csv(args.o+"/"+project_name+"_rpkm.csv", sep="\t")


elif args.map:
	for file_ in allFiles:
		samples = os.path.basename(file_)
		samples_1 = os.path.splitext(samples)[0]
		samples_2 = os.path.splitext(samples_1)[0]
		sample_list.append(samples_2)
		df = pd.read_csv(file_, index_col=None, dtype=str, header=None, sep="\t").assign(filename=samples_2)
		df.columns = ['ACC','genome_length','reads_mapped','reads_unmapped','sample']
		df1 = df[['ACC','genome_length','reads_mapped','sample']]
		df1.set_index('ACC', inplace=True)

		gen_length_key = df1[['genome_length']]
		gen_length_key.to_csv('temp1.csv', sep="\t")

		df2 = df1[['reads_mapped','sample']]

		#print(df2)
		list.append(df2)
	frame2 = pd.concat(list, axis=1, ignore_index=True)
	print(frame2)
#	frame2.to_csv(args.o+"/"+project_name+'_frame2.csv', sep="\t")

	gen_length_key = pd.read_csv("temp1.csv", sep="\t")
	gen_length_key.columns = ['ACC','genome_length']
	gen_length_key.set_index('ACC', inplace=True)
	acc_list.append(gen_length_key.index.values)
	frame3 = pd.concat([gen_length_key,frame2], axis=1, join_axes=[gen_length_key.index])
	print(frame3)
#	frame3.to_csv(args.o+"/"+project_name+'_frame3.csv', sep="\t")


	frame4 = frame3.iloc[0:,1::2]
	print(frame4)
#	frame4.to_csv(args.o+"/"+project_name+'_frame4.csv', sep="\t")

	gen_length_key = pd.read_csv("temp1.csv", sep="\t")
	gen_length_key.columns = ['ACC','genome_length']
	gen_length_key.set_index('ACC', inplace=True)

	counts = pd.concat([gen_length_key,frame4], axis=1, join_axes=[gen_length_key.index])
	print(counts)
	subprocess.call("rm -f temp1.csv", shell=True)

	print(sample_list)
	counts.columns = counts.columns[:1].tolist() + sample_list
	print(counts)

	counts.drop(counts.tail(1).index,inplace=True)
	counts.to_csv(args.o+"/"+project_name+'_counts.csv', sep="\t")


	counts = counts.convert_objects(convert_numeric=True)
	counts.loc['Total',:] = counts.sum(axis=0) / 1000000
	print(counts)
	print(counts.dtypes)
#	counts.to_csv(args.o+"/"+project_name+'1.csv', sep="\t")

	counts['genome_length']['Total'] = 0
	counts_list.append(counts.loc['Total'])
	counts['genome_length'] = counts['genome_length'] / 1000
	counts = counts.add_suffix('_reads')
	counts=counts.rename(columns = {'genome_length_reads':'genome_length'})
	print(counts)
	print(counts_list)
#	counts.to_csv(args.o+"/"+project_name+'2.csv', sep="\t")

	df_test = pd.DataFrame(counts_list)
	df_test.drop('genome_length', axis=1, inplace=True)
	df_test = df_test.add_suffix('_totreads')
	print(df_test)
#	df_test.to_csv(args.o+"/"+project_name+'3.csv', sep="\t")

	try1 = pd.concat([df_test,counts], axis=1, join_axes=[counts.index])
	try1=  try1.sort_values(by=['genome_length'], ascending=[True])

	stacker = try1.stack()
	try1 = stacker.unstack()
	try1 = try1.reindex(sorted(try1.columns), axis=1)
	first_col = try1.pop('genome_length')
	try1.insert(0, 'genome_length', first_col)
	try1.fillna(method='ffill', inplace=True)
	try1 = try1.iloc[1:]
	print(try1)
#	try1.to_csv(args.o+"/"+project_name+'4.csv', sep="\t")

	# RPKM, top = numReads#
	df_top = try1.iloc[0:,1::2]

	# RPKM, bottom = (gen_l/100)(totReads/1000000)#
	df_bottom = try1.iloc[0:,0::2]
	print(df_top)
	print(df_bottom)
	df_bottom.memory_usage(deep=True)

	#RPKM, bottom --> gl*tR#
	#print(df_bottom.iloc[0:,1::1])
	df_bottom_2 = df_bottom.iloc[0:,1::1].multiply(df_bottom["genome_length"], axis="index")
	print(df_bottom_2)


	#RPKM, top/bottom#
	#print(df_top.iloc[0:,0::1])
	df_rpkm = df_top.iloc[0:,0::1].divide(df_bottom_2.values, axis="index")
	df_rpkm.columns = df_rpkm.columns.str.replace('_reads', '', regex=True)
	print(df_rpkm)
	print(acc_list)

	if args.sort_samples and args.sort_gen:
		sorted = pd.read_csv(args.sort_samples, sep="\t")
		print(sorted)
		sorted_list = sorted.columns.tolist()
		print(sorted_list)

		df_rpkm = df_rpkm[sorted_list]

		sorted_y = pd.read_csv(args.sort_gen, sep="\t")
		print(sorted_y)
		sorted_list_y = sorted_y.columns.tolist()
		print(sorted_list_y)

		df_rpkm = df_rpkm.reindex(sorted_list_y)
#		df_rpkm = df_rpkm.T
		print(df_rpkm)
		df_rpkm = np.log10(df_rpkm)
		df_rpkm[df_rpkm < 0] = 0
		df_rpkm.to_csv(args.o+"/"+project_name+"_rpkm.csv", sep="\t")





		#Heatmap sorted by Ocean and depth#
		if args.colors:
			if args.colors == 'plasma':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFFF99','#efe350ff','#f7cb44ff','#f9b641ff','#f9a242ff',\
				'#f68f46ff','#eb8055ff','#de7065ff','#cc6a70ff','#b8627dff','#a65c85ff','#90548bff','#7e4e90ff','#6b4596ff','#593d9cff',\
				'#403891ff','#253582ff','#13306dff','#0c2a50ff','#042333ff'], N=10000000)
			elif args.colors == 'viridis':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFFF99','#DCE319FF','#B8DE29FF','#95D840FF','#73D055FF',\
				'#55C667FF','#3CBB75FF','#29AF7FFF','#20A387FF','#1F968BFF','#238A8DFF','#287D8EFF','#2D708EFF','#33638DFF','#39568CFF',\
				'#404788FF','#453781FF','#482677FF','#481567FF','#440154FF'], N=10000000)
			elif args.colors == 'blue':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#99FFFF','#6699FF','#0000CC','#000099','#000066'], N=10000000)
			elif args.colors == 'red':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFCCCC','#FF6666','#CC3333','#990000','#660000'], N=10000000)
			elif args.colors == 'green':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#CCFFCC','#66CC66','#339933','#006600','#003300'], N=10000000)
			leg_color = plt.pcolor(df_rpkm, cmap=colormap_1)
			plt.yticks(np.arange(0.2, len(df_rpkm.index), 1), df_rpkm.index)
			plt.xticks(np.arange(0.2, len(df_rpkm.columns), 1), df_rpkm.columns)
			plt.xticks(fontsize=1.5, rotation=90)
			if args.phylo_colors:
				ord_list = []
				color_phy_list = []
				phylo = open(args.phylo_colors, "r")
				for lines in phylo.readlines():
					line = lines.rstrip()
					tabs = line.split("\t")
					ids = tabs[0]
					ord = tabs[1]
					color = tabs[2]
					ord_list.append(ord)
					ord_list = [int(i) for i in ord_list]
					color_phy_list.append(color)
					color_phy_list = [str(i) for i in color_phy_list]
#                    print(ord_list)
#                    print(color_phy_list)
				for val,val2 in zip(ord_list,color_phy_list):
					plt.gca().get_yticklabels()[val].set_color(val2)
			else:
				pass
			if args.xticks == 'off':
				plt.xticks([])
			else:
				pass
			if args.yticks == 'off':
				plt.yticks([])
			else:
				pass
			plt.yticks(fontsize=0.0005)
			plt.gca().invert_yaxis()
			plt.tight_layout()
			legend = plt.colorbar(leg_color)
        #plt.show()
			date = time.strftime("%m.%d.%Y")
			plt.savefig(args.o+"/"+project_name+'_rpkm_heat_'+date+'.png',dpi=1100)
		else:
			colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFFF99','#efe350ff','#f7cb44ff','#f9b641ff','#f9a242ff',\
			'#f68f46ff','#eb8055ff','#de7065ff','#cc6a70ff','#b8627dff','#a65c85ff','#90548bff','#7e4e90ff','#6b4596ff','#593d9cff',\
			'#403891ff','#253582ff','#13306dff','#0c2a50ff','#042333ff'], N=10000000)
			#norm = Normalize(vmin=min(df_rpkm),vmax=max(df_rpkm))
			leg_color = plt.pcolor(df_rpkm, cmap=colormap_1)
			plt.yticks(np.arange(0.2, len(df_rpkm.index), 1), df_rpkm.index)
			plt.xticks(np.arange(0.2, len(df_rpkm.columns), 1), df_rpkm.columns)
			plt.xticks(fontsize=1.5, rotation=90)
			if args.phylo_colors:
				ord_list = []
				color_phy_list = []
				phylo = open(args.phylo_colors, "r")
				for lines in phylo.readlines():
					line = lines.rstrip()
					tabs = line.split("\t")
					ids = tabs[0]
					ord = tabs[1]
					color = tabs[2]
					ord_list.append(ord)
					ord_list = [int(i) for i in ord_list]
					color_phy_list.append(color)
					color_phy_list = [str(i) for i in color_phy_list]
#                    print(ord_list)
#                    print(color_phy_list)
				for val,val2 in zip(ord_list,color_phy_list):
					plt.gca().get_xticklabels()[val].set_color(val2)
			else:
				pass
			if args.xticks == 'off':
				plt.xticks([])
			else:
				pass
			if args.yticks == 'off':
				plt.yticks([])
			else:
				pass
			plt.yticks(fontsize=0.05)
			plt.gca().invert_yaxis()
			plt.tight_layout()
			legend = plt.colorbar(leg_color)
			#plt.show()
			date = time.strftime("%m.%d.%Y")
			plt.savefig(args.o+"/"+project_name+'_rpkm_heat_'+date+'.png',dpi=900)

	elif args.sort_samples:
		sorted = pd.read_csv(args.sort_samples, sep="\t")
		print(sorted)
		sorted_list = sorted.columns.tolist()
		print(sorted_list)

		df_rpkm = df_rpkm[sorted_list]
		print(df_rpkm)
		df_rpkm = np.log10(df_rpkm)
		df_rpkm[df_rpkm < 0] = 0
		df_rpkm.to_csv(args.o+"/"+project_name+"_rpkm.csv", sep="\t")


		#Heatmap sorted by Ocean and depth#
		if args.colors:
			if args.colors == 'plasma':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFFF99','#efe350ff','#f7cb44ff','#f9b641ff','#f9a242ff',\
				'#f68f46ff','#eb8055ff','#de7065ff','#cc6a70ff','#b8627dff','#a65c85ff','#90548bff','#7e4e90ff','#6b4596ff','#593d9cff',\
				'#403891ff','#253582ff','#13306dff','#0c2a50ff','#042333ff'], N=10000000)
			elif args.colors == 'viridis':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFFF99','#DCE319FF','#B8DE29FF','#95D840FF','#73D055FF',\
				'#55C667FF','#3CBB75FF','#29AF7FFF','#20A387FF','#1F968BFF','#238A8DFF','#287D8EFF','#2D708EFF','#33638DFF','#39568CFF',\
				'#404788FF','#453781FF','#482677FF','#481567FF','#440154FF'], N=10000000)
			elif args.colors == 'blue':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#99FFFF','#6699FF','#0000CC','#000099','#000066'], N=10000000)
			elif args.colors == 'red':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFCCCC','#FF6666','#CC3333','#990000','#660000'], N=10000000)
			elif args.colors == 'green':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#CCFFCC','#66CC66','#339933','#006600','#003300'], N=10000000)
			#norm = Normalize(vmin=min(df_rpkm),vmax=max(df_rpkm))
			leg_color = plt.pcolor(df_rpkm, cmap=colormap_1)
			plt.yticks(np.arange(0.2, len(df_rpkm.index), 1), df_rpkm.index)
			plt.xticks(np.arange(0.2, len(df_rpkm.columns), 1), df_rpkm.columns)
			plt.xticks(fontsize=1.5, rotation=90)
			if args.phylo_colors:
				ord_list = []
				color_phy_list = []
				phylo = open(args.phylo_colors, "r")
				for lines in phylo.readlines():
					line = lines.rstrip()
					tabs = line.split("\t")
					ids = tabs[0]
					ord = tabs[1]
					color = tabs[2]
					ord_list.append(ord)
					ord_list = [int(i) for i in ord_list]
					color_phy_list.append(color)
					color_phy_list = [str(i) for i in color_phy_list]
#                    print(ord_list)
#                    print(color_phy_list)
				for val,val2 in zip(ord_list,color_phy_list):
					plt.gca().get_xticklabels()[val].set_color(val2)
			else:
				pass
			if args.xticks == 'off':
				plt.xticks([])
			else:
				pass
			if args.yticks == 'off':
				plt.yticks([])
			else:
				pass
			plt.yticks(fontsize=0.05)
			plt.gca().invert_yaxis()
			plt.gca().invert_yaxis()
			plt.tight_layout()
			legend = plt.colorbar(leg_color)
			#plt.show()
			date = time.strftime("%m.%d.%Y")
			plt.savefig(args.o+"/"+project_name+'_rpkm_heat_'+date+'.png',dpi=900)
		else:
			colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFFF99','#efe350ff','#f7cb44ff','#f9b641ff','#f9a242ff',\
			'#f68f46ff','#eb8055ff','#de7065ff','#cc6a70ff','#b8627dff','#a65c85ff','#90548bff','#7e4e90ff','#6b4596ff','#593d9cff',\
			'#403891ff','#253582ff','#13306dff','#0c2a50ff','#042333ff'], N=10000000)
			#norm = Normalize(vmin=min(df_rpkm),vmax=max(df_rpkm))
			leg_color = plt.pcolor(df_rpkm, cmap=colormap_1)
			plt.yticks(np.arange(0.2, len(df_rpkm.index), 1), df_rpkm.index)
			plt.xticks(np.arange(0.2, len(df_rpkm.columns), 1), df_rpkm.columns)
			plt.xticks(fontsize=1.5, rotation=90)
			if args.phylo_colors:
				ord_list = []
				color_phy_list = []
				phylo = open(args.phylo_colors, "r")
				for lines in phylo.readlines():
					line = lines.rstrip()
					tabs = line.split("\t")
					ids = tabs[0]
					ord = tabs[1]
					color = tabs[2]
					ord_list.append(ord)
					ord_list = [int(i) for i in ord_list]
					color_phy_list.append(color)
					color_phy_list = [str(i) for i in color_phy_list]
#                    print(ord_list)
#                    print(color_phy_list)
				for val,val2 in zip(ord_list,color_phy_list):
					plt.gca().get_yticklabels()[val].set_color(val2)
			else:
				pass
			if args.xticks == 'off':
				plt.xticks([])
			else:
				pass
			if args.yticks == 'off':
				plt.yticks([])
			else:
				pass
			plt.yticks(fontsize=0.05)
			plt.gca().invert_yaxis()
			plt.tight_layout()
			legend = plt.colorbar(leg_color)
			#plt.show()
			date = time.strftime("%m.%d.%Y")
			plt.savefig(args.o+"/"+project_name+'_rpkm_heat_'+date+'.png',dpi=900)

	elif args.sort_gen:
		sorted_y = pd.read_csv(args.sort_gen, sep="\t")
		print(sorted_y)
		sorted_list_y = sorted_y.columns.tolist()
		print(sorted_list_y)

		df_rpkm = df_rpkm.reindex(sorted_list_y)
#		df_rpkm = df_rpkm.T
		df_rpkm = np.log10(df_rpkm)
		df_rpkm[df_rpkm < 0] = 0
		df_rpkm.to_csv(args.o+"/"+project_name+"_rpkm.csv", sep="\t")

		#Heatmap sorted by Ocean and depth#
		if args.colors:
			if args.colors == 'plasma':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFFF99','#efe350ff','#f7cb44ff','#f9b641ff','#f9a242ff',\
				'#f68f46ff','#eb8055ff','#de7065ff','#cc6a70ff','#b8627dff','#a65c85ff','#90548bff','#7e4e90ff','#6b4596ff','#593d9cff',\
				'#403891ff','#253582ff','#13306dff','#0c2a50ff','#042333ff'], N=10000000)
			elif args.colors == 'viridis':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFFF99','#DCE319FF','#B8DE29FF','#95D840FF','#73D055FF',\
				'#55C667FF','#3CBB75FF','#29AF7FFF','#20A387FF','#1F968BFF','#238A8DFF','#287D8EFF','#2D708EFF','#33638DFF','#39568CFF',\
				'#404788FF','#453781FF','#482677FF','#481567FF','#440154FF'], N=10000000)
			elif args.colors == 'blue':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#99FFFF','#6699FF','#0000CC','#000099','#000066'], N=10000000)
			elif args.colors == 'red':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFCCCC','#FF6666','#CC3333','#990000','#660000'], N=10000000)
			elif args.colors == 'green':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#CCFFCC','#66CC66','#339933','#006600','#003300'], N=10000000)

			leg_color = plt.pcolor(df_rpkm, cmap=colormap_1)
			plt.yticks(np.arange(0.2, len(df_rpkm.index), 1), df_rpkm.index)
			plt.xticks(np.arange(0.2, len(df_rpkm.columns), 1), df_rpkm.columns)
			plt.xticks(fontsize=1.5, rotation=90)
			if args.phylo_colors:
				ord_list = []
				color_phy_list = []
				phylo = open(args.phylo_colors, "r")
				for lines in phylo.readlines():
					line = lines.rstrip()
					tabs = line.split("\t")
					ids = tabs[0]
					ord = tabs[1]
					color = tabs[2]
					ord_list.append(ord)
					ord_list = [int(i) for i in ord_list]
					color_phy_list.append(color)
					color_phy_list = [str(i) for i in color_phy_list]
#                    print(ord_list)
#                    print(color_phy_list)
				for val,val2 in zip(ord_list,color_phy_list):
					plt.gca().get_xticklabels()[val].set_color(val2)
			else:
				pass
			if args.xticks == 'off':
				plt.xticks([])
			else:
				pass
			if args.yticks == 'off':
				plt.yticks([])
			else:
				pass
			plt.yticks(fontsize=0.05)
			plt.gca().invert_yaxis()
			plt.tight_layout()
			legend = plt.colorbar(leg_color)
			#plt.show()
			date = time.strftime("%m.%d.%Y")
			plt.savefig(args.o+"/"+project_name+'_rpkm_heat_'+date+'.png',dpi=900)
		else:
			colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFFF99','#efe350ff','#f7cb44ff','#f9b641ff','#f9a242ff',\
			'#f68f46ff','#eb8055ff','#de7065ff','#cc6a70ff','#b8627dff','#a65c85ff','#90548bff','#7e4e90ff','#6b4596ff','#593d9cff',\
			'#403891ff','#253582ff','#13306dff','#0c2a50ff','#042333ff'], N=10000000)
			#norm = Normalize(vmin=min(df_rpkm),vmax=max(df_rpkm))
			leg_color = plt.pcolor(df_rpkm, cmap=colormap_1)
			plt.yticks(np.arange(0.2, len(df_rpkm.index), 1), df_rpkm.index)
			plt.xticks(np.arange(0.2, len(df_rpkm.columns), 1), df_rpkm.columns)
			plt.xticks(fontsize=1.5, rotation=90)
			if args.phylo_colors:
				ord_list = []
				color_phy_list = []
				phylo = open(args.phylo_colors, "r")
				for lines in phylo.readlines():
					line = lines.rstrip()
					tabs = line.split("\t")
					ids = tabs[0]
					ord = tabs[1]
					color = tabs[2]
					ord_list.append(ord)
					ord_list = [int(i) for i in ord_list]
					color_phy_list.append(color)
					color_phy_list = [str(i) for i in color_phy_list]
#                    print(ord_list)
#                    print(color_phy_list)
				for val,val2 in zip(ord_list,color_phy_list):
					plt.gca().get_xticklabels()[val].set_color(val2)
			else:
				pass
			if args.xticks == 'off':
				plt.xticks([])
			else:
				pass
			if args.yticks == 'off':
				plt.yticks([])
			else:
				pass
			plt.yticks(fontsize=0.05)
			plt.gca().invert_yaxis()
			plt.tight_layout()
			legend = plt.colorbar(leg_color)
			#plt.show()
			date = time.strftime("%m.%d.%Y")
			plt.savefig(args.o+"/"+project_name+'_rpkm_heat_'+date+'.png',dpi=900)
	else:

		df_rpkm = np.log10(df_rpkm)
		df_rpkm[df_rpkm < 0] = 0
		df_rpkm.to_csv(args.o+"/"+project_name+"_rpkm.csv", sep="\t")

		if args.colors:
			if args.colors == 'plasma':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFFF99','#efe350ff','#f7cb44ff','#f9b641ff','#f9a242ff',\
				'#f68f46ff','#eb8055ff','#de7065ff','#cc6a70ff','#b8627dff','#a65c85ff','#90548bff','#7e4e90ff','#6b4596ff','#593d9cff',\
				'#403891ff','#253582ff','#13306dff','#0c2a50ff','#042333ff'], N=10000000)
			elif args.colors == 'viridis':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFFF99','#DCE319FF','#B8DE29FF','#95D840FF','#73D055FF',\
				'#55C667FF','#3CBB75FF','#29AF7FFF','#20A387FF','#1F968BFF','#238A8DFF','#287D8EFF','#2D708EFF','#33638DFF','#39568CFF',\
				'#404788FF','#453781FF','#482677FF','#481567FF','#440154FF'], N=10000000)
			elif args.colors == 'blue':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#99FFFF','#6699FF','#0000CC','#000099','#000066'], N=10000000)
			elif args.colors == 'red':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFCCCC','#FF6666','#CC3333','#990000','#660000'], N=10000000)
			elif args.colors == 'green':
				colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#CCFFCC','#66CC66','#339933','#006600','#003300'], N=10000000)
			#norm = Normalize(vmin=min(df_rpkm),vmax=max(df_rpkm))
			leg_color = plt.pcolor(df_rpkm, cmap=colormap_1)
			plt.yticks(np.arange(0.2, len(df_rpkm.index), 1), df_rpkm.index)
			plt.xticks(np.arange(0.2, len(df_rpkm.columns), 1), df_rpkm.columns)
			plt.xticks(fontsize=2, rotation=90)
			if args.phylo_colors:
				ord_list = []
				color_phy_list = []
				phylo = open(args.phylo_colors, "r")
				for lines in phylo.readlines():
					line = lines.rstrip()
					tabs = line.split("\t")
					ids = tabs[0]
					ord = tabs[1]
					color = tabs[2]
					ord_list.append(ord)
					ord_list = [int(i) for i in ord_list]
					color_phy_list.append(color)
					color_phy_list = [str(i) for i in color_phy_list]
#                    print(ord_list)
#                    print(color_phy_list)
				for val,val2 in zip(ord_list,color_phy_list):
					plt.gca().get_xticklabels()[val].set_color(val2)
			else:
				pass
			if args.xticks == 'off':
				plt.xticks([])
			else:
				pass
			if args.yticks == 'off':
				plt.yticks([])
			else:
				pass
			plt.yticks(fontsize=2)
			plt.gca().invert_yaxis()
			plt.tight_layout()
			legend = plt.colorbar(leg_color)
			#plt.show()
			date = time.strftime("%m.%d.%Y")
			plt.savefig(args.o+"/"+project_name+'_rpkm_heat_'+date+'.png',dpi=900)
		else:
			colormap_1 = LinearSegmentedColormap.from_list('colorbar', ['#FFFF99','#efe350ff','#f7cb44ff','#f9b641ff','#f9a242ff',\
			'#f68f46ff','#eb8055ff','#de7065ff','#cc6a70ff','#b8627dff','#a65c85ff','#90548bff','#7e4e90ff','#6b4596ff','#593d9cff',\
			'#403891ff','#253582ff','#13306dff','#0c2a50ff','#042333ff'], N=10000000)
			#norm = Normalize(vmin=min(df_rpkm),vmax=max(df_rpkm))
			leg_color = plt.pcolor(df_rpkm, cmap=colormap_1)
			plt.yticks(np.arange(0.2, len(df_rpkm.index), 1), df_rpkm.index)
			plt.xticks(np.arange(0.2, len(df_rpkm.columns), 1), df_rpkm.columns)
			plt.xticks(fontsize=1.5, rotation=90)
			if args.phylo_colors:
				ord_list = []
				color_phy_list = []
				phylo = open(args.phylo_colors, "r")
				for lines in phylo.readlines():
					line = lines.rstrip()
					tabs = line.split("\t")
					ids = tabs[0]
					ord = tabs[1]
					color = tabs[2]
					ord_list.append(ord)
					ord_list = [int(i) for i in ord_list]
					color_phy_list.append(color)
					color_phy_list = [str(i) for i in color_phy_list]
#                    print(ord_list)
#                    print(color_phy_list)
				for val,val2 in zip(ord_list,color_phy_list):
					plt.gca().get_xticklabels()[val].set_color(val2)
			else:
				pass
			if args.xticks == 'off':
				plt.xticks([])
			else:
				pass
			if args.yticks == 'off':
				plt.yticks([])
			else:
				pass
			plt.yticks(fontsize=0.05)
			plt.gca().invert_yaxis()
			plt.tight_layout()
			legend = plt.colorbar(leg_color)
			#plt.show()
			date = time.strftime("%m.%d.%Y")
			plt.savefig(args.o+"/"+project_name+'_rpkm_heat_'+date+'.png',dpi=900)
