#!/nfs/hicran/home/fkrinner/private/bin/python
import sys
from sys import argv
import os

#mc_paths = 'insert_MC.dat'
#mc_paths = 'insert_MC_4_waves.dat'
#mc_paths = 'insert_MC_only_0mp.dat'
mc_paths = 'insert_standard_isobar.dat'
get_self=False
card_in = argv[1]
if len(argv)>2:
	path = argv[2]
	get_self=True
	if not path.endswith('/'):
		path = path+'/'
afterset = "/0.14077-0.19435/wMC_tree_isobarred.root_'"
suffix=" *PH_BINS_SUFFIX   '.root'"
binstring = ' *SORTMASSBINS 1.500 1.540 0.0 0.0 0.040'

chunks = card_in.split('.')
card_out = chunks[0] + '_MC.'+chunks[1]
inCard = open(card_in,'r')
outCard = open(card_out,'w')
insert = open(mc_paths,'r')
outCard.write('C CARD_FOR_MONTE_CARLO\n')
for line in inCard.readlines():
	chunks = line.split()
	if chunks[0] in ['IS_TRIGGERED', 'IS_IN_TARGET', 'IS_EXCLUSIVE', 'IS_IN_T', 'CENTRAL_PROD_VETO', 'IS_IN_BEAM_TIME', 'RICH_VETO', 'CEDAR_VETO', 'IS_IN_DELTA_PHI', 'CORRECT_NBR_RPD_TRACKS', 'IS_PLANAR', 'IS_PLANAR_EXTENDED', '*PH_BINS_PREFIX']:
		outCard.write('C '+line)
	elif chunks[0] == '*PH_BINS_SUFFIX':
		if get_self:
			for fn in os.listdir(path):
				outCard.write(" *PH_BINS_PREFIX   '"+path+fn+afterset+'\n')
				outCard.write(suffix+'\n')
			outCard.write(binstring+'\n')
		else:	
			for line_ins in insert.readlines():
				outCard.write(line_ins)
	elif chunks[0] == '*SORTMASSBINS':
		pass
	else:
		outCard.write(line)
outCard.write(" NO_ACC\n")
outCard.close()
inCard.close()
insert.close()




