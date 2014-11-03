from sys import argv
from os import system

MAX_F0 = 61
MAX_RHO = 55

def get_new_onb_wave(wave,count):
	"""
	Gets the name of wave in the new ONB
	"""
	countString=str(count)
	while len(countString)<4:
		countString = '0'+countString
	if 'f0_' in wave:
		new_isob = 'f0No'+countString
	elif 'rho_' in wave:
		new_isob = 'rhoNo'+countString
	else: # not a wave to be transformed
		return wave
	chunks = wave.split()
	chunks[1] = new_isob
	outWave = ''
	for chunk in chunks:
		outWave+=chunk+' '
	while len(outWave)<60:
		outWave+=' '
	return outWave



try:
	incard = argv[1]
except IndexError:
	incard = raw_input("card_name")

if incard.startswith("card_") and incard.endswith('.dat'):
	print "Card name in standard formt, use automatically generated name:"
	outcard = incard[:-4]+'_new_ONB.dat'
	print outcard
else:
	outcard = raw_input("Specify the name of the output card:")

rhocount=0
f0count=0


with open(incard,'r') as inFile:
	with open(outcard,'w') as outFile:
		outFile.write("C Cards generated by 'create_new_ONB.py' from " + incard)
		for line in inFile.readlines():	
			if ('f0_' in line or 'rho_' in line) and 'IWAVENAM' in line and not line.startswith('C'):
				wave = line.split("'")[1]
				comment= ''
				if 'f0_' in wave:
					f0count+=1
					outWave = get_new_onb_wave(wave,f0count)
					if f0count > MAX_F0:
						comment = 'C'
				if 'rho_' in wave:
					rhocount+=1
					outWave = get_new_onb_wave(wave,rhocount)
					if rhocount > MAX_RHO:
						comment = 'C'
				outFile.write(comment+line.replace(wave,outWave))
			elif 'addwave' in line:	
				outFile.write(line.replace('addwave','addwave_new_ONB'))
			else:
				outFile.write(line)
				
							
system("create_addwave.py "+outcard)			
			

