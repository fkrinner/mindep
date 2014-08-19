from sys import argv
from os.path import splitext
from os import system

N_BLOCK_FLATWAVE      = 1
N_BLOCK_NATURAL_WAVES = 2 # Blocknumber for the natural waves
N_BLOCK_NEGATIVE_REFL = 3 # Blocknumber of the neg. refl. waves

try:
	inFile_name = argv[1]
except IndexError:
	inFile_name = raw_input("Input card:")

waves_to_ask=[
'1-(0-+)0+ 0++ pi S                                     ',
'1-(1++)0+ 0++ pi P                                     ',
'1-(2-+)0+ 0++ pi D                                     ',
'1-(1++)0+ rho pi S                                          ',
'1-(2++)1+ rho pi D                                          ',
'1-(1++)0+ f2 pi P                                           ']

isobars = {
'1-(0-+)0+ 0++ pi S                                     ':['1-(0-+)0+ (pipi)_S pi S                                     ','1-(0-+)0+ f0(980) pi S                                      ','1-(0-+)0+ f0(1500) pi S                                     '],
'1-(1++)0+ 0++ pi P                                     ':['1-(1++)0+ (pipi)_S pi P                                     ','1-(1++)0+ f0(980) pi P                                      '],
'1-(2-+)0+ 0++ pi D                                     ':['1-(2-+)0+ (pipi)_S pi D                                     ','1-(2-+)0+ f0(980) pi D                                      '],
'1-(1++)0+ rho pi S                                          ':['1-(1++)0+ rho pi S                                          '],
'1-(2++)1+ rho pi D                                          ':['1-(2++)1+ rho pi D                                          '],
'1-(1++)0+ f2 pi P                                           ':['1-(1++)0+ f2 pi P                                           ']}

to_do = {}

for wave in waves_to_ask:
	print wave
	print "d: de-isobarred"
	print "i: isobarred"
	print "n: not used"
	while True:
		job = raw_input("What to do with "+wave+"?\n")
		if job == 'i':
			to_do[wave] = 'i'
			break
		if job == 'd':
			to_do[wave] = 'd'
			break
		if job == 'n':
			to_do[wave] = 'n'
			break
	print "-------------------------"	

try: 
	config_string = argv[2]
except IndexError:
	print "No outfile given. Use config_string"
	config_string=''
	for wave in waves_to_ask:
		config_string+=to_do[wave]
outFile_name = splitext(inFile_name)[0]+'_'+config_string+splitext(inFile_name)[1]
	
inFile = open(inFile_name,'r')
outFile= open(outFile_name,'w')

addwave_name = outFile_name.replace('card_','addwave_')
if addwave_name == outFile_name:
	print "Warning: No separate name for the 'addwave' file, usd default 'addwave_default_name.dat'"
	addwave_name = 'addwave_default_name.dat'

nBlock =0
write = True

for line in inFile.readlines():
	if '*OPEN70' in line:
		outFile.write("  *OPEN70                '"+addwave_name+"'\n")
	elif '*BLOCKRANK' in line:
		nBlock+=1
		if not nBlock == N_BLOCK_FLATWAVE:
			write = False
		if not nBlock == N_BLOCK_NEGATIVE_REFL:
			outFile.write(line)
		if nBlock == N_BLOCK_NATURAL_WAVES:
			for wave in waves_to_ask:
				if to_do[wave] == 'i':
					for isobar in isobars[wave]:
						outFile.write("*IWAVENAM '"+isobar+"'    0     0     0\n")
				if to_do[wave] == 'd':
					if '0++' in wave:
						steps = open('de_isobarred_f0.dat','r')
						for step in steps.readlines():
							outFile.write("*IWAVENAM '"+wave.replace('0++',step.split()[0])[:60]+"'    0     0     0     "+step.split()[1]+"\n")
						steps.close()
					if 'rho' in wave:
						steps = open('de_isobarred_rho.dat','r')
						for step in steps.readlines():
							outFile.write("*IWAVENAM '"+wave.replace('rho',step.split()[0])[:60]+"'    0     0     0     "+step.split()[1]+"\n")
						steps.close()
					if 'f2' in wave:
						steps = open('de_isobarred_f2.dat','r')
						for step in steps.readlines():
							outFile.write("*IWAVENAM '"+wave.replace('f2',step.split()[0])[:60]+"'    0     0     0     "+step.split()[1]+"\n")
						steps.close()
	elif '*BLOCKEND' in line:
		write = True
		if not nBlock == N_BLOCK_NEGATIVE_REFL:
			outFile.write(line)
	elif write:
		outFile.write(line)

outFile.close()
inFile.close()
system('python ./create_addwave.py '+outFile_name)

