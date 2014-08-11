#!/nfs/hicran/home/fkrinner/private/bin/python
import sys
from sys import argv

'1-(1++)0+ rho pi D                                          '
def checkWaveName(wave):
	if len(wave)>60:
		return False
	try:
		int(wave[0])
	except:
		return False
	if not wave[1] in ['-','+']:
		return False
	if not wave[2] == '(':
		return False
	try:
		int(wave[3])
	except:
		return False
	if not wave[4:6] in ['++','-+','+-','--']:
		return False
	if not wave[6] == ')':
		return False
	try:
		int(wave[7])
	except:
		return False
	if not wave[8] in ['-','+']:
		return False
	chunks=wave.split()
	if not chunks[1] in ['rho','f2','f0(980)','f0(1500','(pipi)_S']:
		return False
	if not chunks[2] == 'pi':
		return False
	try:
		chunks[4]
	except:
		return True
	return False


name = argv[1]
deisobar_waves=[]

addwavefile="addwave_"+name+".dat"

for i in range(2,len(argv)):
	deisobar_waves.append(argv[i])
	print "Deisobar: "+argv[i]

newWaves=[]
for wave in deisobar_waves:
	if len(wave) > 60:
		print "Name of wave too long. Exit."
		sys.exit(1)
	while len(wave) < 60:
		wave= wave+' '
	
	newWaves.append(wave)

deisobar_waves=newWaves[:]
#for wave in deisobar_waves:
#	print "'"+wave+"'"


card=open("card_"+name+".dat","w")
template=open("template_card.dat","r")

already_done=[] 

for line in template.readlines():
	if not 'addwavefile' in line and not 'ADD DEISOBARRED WAVES HERE' in line and not '*IWAVENAM' in line and not 'Template' in line:
		card.write(line)
	if 'addwavefile' in line:
		card.write(line.replace('addwavefile',addwavefile))
	if '*IWAVENAM' in line:
		actWave=line.split("'")[1]
#		print "'"+actWave+"'"
		if actWave in deisobar_waves:
			card.write("C"+line)
		else:
			card.write(line)
	if 'Template' in line:
		card.write("C The following waves were desiobarred:\n")
		for wve in deisobar_waves:
			card.write("C "+wve+'\n')
	if 'ADD DEISOBARRED WAVES HERE' in line:
		for wave in deisobar_waves:
			card.write("C Deisobar "+wave+"\n")
			chunks=wave.split()
			prefix="*IWAVENAM '"
			jpc=chunks[0]+' '
			suffix=' '+chunks[2]+' '+chunks[3]
			if chunks[1] == 'f2':
				openFile='de_isobarred_f2.dat'
				isobar='f2'
			elif chunks[1] == 'rho':
				openFile = 'de_isobarred_rho.dat'
				isobar='rho'
			elif chunks[1] in ['f0(980)','f0(1500)','(pipi)_S']:
				openFile = 'de_isobarred_f0.dat'
				isobar='f0'
			else:
				print 'Error: Isobar cannot be deisobarred.'
				sys.exit(1)
			checkWave=chunks[0]+isobar+chunks[2]+chunks[3]
			if not checkWave in already_done:
				already_done.append(checkWave)
				stepFile=open(openFile,'r')
				for step in stepFile.readlines():	
					stepThresh=step.split()
					wavenew=jpc+stepThresh[0]+' '+chunks[2]+' '+chunks[3]
					while len(wavenew)<60:
						wavenew=wavenew+' '
					card.write(prefix+wavenew+"'    0     0     0   "+stepThresh[1]+'\n')
			else:
				card.write("C JPC already done\n")
template.close()
card.close()
card=open("card_"+name+".dat","r")
addwave=open(addwavefile,'w')
for line in card.readlines():
	if line.strip().startswith('*IWAVENAM'):
		chunks=line.strip().split("'")
		addwave.write("*ADDWAVE  '"+chunks[1]+"'\n")
addwave.write("*ADDWAVE  '1-(2++)2- f2 pi P                                           '\n*ADDWAVE  '1-(2++)1- rho pi D                                          '")#For some reason, the second to last integral is doubled and the last one omitted, so none of them may appear in the fit.
addwave.close()
card.close()





