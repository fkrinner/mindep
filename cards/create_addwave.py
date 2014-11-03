#!/nfs/hicran/home/fkrinner/private/bin/python
import sys
from sys import argv
from sys import exit


try:
	name = argv[1]
except:
	name = raw_input('name:')

try:
	card = open('card_'+name+'.dat','r')
except:
	print "'card_"+name+".dat' does not exists, try card alone"
	try:
		card = open(name,'r')
	except:
		print "Card '"+name+"' does not exist"
		exit(1)

for line in card.readlines():
	if '*OPEN70' in line:
		addwavename = line.strip().split()[1][1:-1]
		addwave = open(addwavename,'w')
	if line.strip().startswith('*IWAVENAM') and not "_NAMDEP" in line:
		chunks = line.strip().split("'")
		addwave.write("*ADDWAVE  '"+chunks[1]+"'\n")
	if line.strip().startswith('*IWAVENAM_NAMDEP'):
		addwave.write(line.replace("*IWAVENAM_NAMDEP","*ADDWAVE_NAMDEP"))


addwave.write("*ADDWAVE  '1-(2++)2- f2 pi P                                           '\n*ADDWAVE  '1-(2++)1- rho pi D                                          '")#For some reason, the second to last integral is doubled and the last one omitted, so none of them may appear in the fit.

card.close()
addwave.close()
print "Created 'addwave.dat' for card_"+name+'.dat'



