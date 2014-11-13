import os
import random
import shutil
import time
import sys
from shutil import copyfile
import analyzeQstat
from analyzeQstat import getRunningJobs

#executable='/nfs/hicran/project/compass/analysis/fkrinner/workDir/compassPWAbin_new/bin/pwanew_3pic_compass_2008florian3_dfunc.static'
executable='/nfs/hicran/project/compass/analysis/fkrinner/workDir/compassPWAbin_big/bin/pwanew_3pic_compass_2008florian3_dfunc.static'

def getRightId(mMin,width,m):					# The calcualtion has to be inverse to the one done in the 'run_pwa_...' script to get the ids right
	"""Detmins the job ID for a given mass from the minimum mass, and the bin width"""
	return int((float(m)-float(mMin))/float(width)+1+0.5) 	# The +0.5 is needed to get the rounding right

def submit_pwa(target,intdir,source,logdir,wrampdir,cardfolder,card,mMin,mMax,binWidth,nstage,tBinsAct,seeds,mappingName='map',MC_Fit=False,treename=None, wrampmode = False, COMPENSATE_AMP = '0', PRINT_CMD_ONLY=False):
	"""Submits the COMPASSPWA fitter to the E18 batch system"""
	jobIDs=[]
	MC_char=''
	
#Set the event tree name:
	pwaIn="'USR52mb'" #Default for fits
	if MC_Fit: 
		MC_char='C '
		pwaIn = "'wMC'" #Set for Monte carlo fits
	if treename: #Override, if an explicit tree name is given
		pwaIn = treename

# The thing with the mapping file can probably be taken out, but I am too lazy right now...)
	jobnameprefix='pwa'
	reloop=False 	# Set reloop, if 'on the fly' resubmission is wanted. At the moment, reloop is False by default, since fits are performed with the './perform_PWA.py' script
			# Which resibmits after all jobs have completed. Probably some time could be saved, if reloop is reactivated, but some effort has to be made, things will probably be messed up

	iseed_random=0
	nseed_random=40

	if wrampmode:
		seeds=['404']	 # Put in a wrampmode, that looks for nonexisting 'wramp' files, that shoult be there, then only submits the jobs, where the wrampfile is missing with seed '404'

	nrep=1 #Leave this at one, chance at position <1> if reloop is wanted

#Sets the stage
	if nstage == 0:	# Submits all seeds, waits for the first seed to write the amplitudes, then runs all other seeds
		iNfits_min=0
		iNfits_max=len(seeds)

	if  nstage == 1: # Submits only the first seed.
		iNfits_min=0
		iNfits_max=1

	if  nstage == 2: # Submits all but the first seed, does not write amplitudes
		iNfits_min=0
		iNfits_max=len(seeds)

	if  nstage == 3: # Resubmits killed, unfinished jobs.
		iNfits_min=0
		iNfits_max=len(seeds)
		if reloop: # position <1> is here. Also set reloop to True, if wanted
			nrep=100

	if not os.path.exists(logdir):
		os.makedirs(logdir)

	if not os.path.exists(target):
		os.makedirs(target)

	for irep in range(0,nrep):
		if nstage<3 and not wrampmode: #Do NOT run several different fits at once, this will mess up the mapping file. (Does not matter, if reloop == False)
			mappingFile=open(mappingName,'w')
		elif not wrampmode:
			mappingFile=open(mappingName,'r')
			mappingsStore=mappingFile.readlines()
			mappingFile.close()
			mappingFile=open(mappingName,'a')
		for l in range(len(tBinsAct)):
			lowerEdge=tBinsAct[l][0]
			upperEdge=tBinsAct[l][1]

			workdirTbin=target+'/'+lowerEdge+'-'+upperEdge+'/'

			if not os.path.exists(workdirTbin):
				os.makedirs(workdirTbin)
			
			if not os.path.exists(wrampdir):
				os.makedirs(wrampdir)

	#			copyfile(intdir+'/'+lowerEdge+'-'+upperEdge+'/nmcset.dat',workdirTbin+'/nmcset_'+lowerEdge+'-'+upperEdge+'.dat')	

#Determine the addwave file	
			readCard=open(cardfolder+'/'+card,'r')
			for line in readCard.readlines():
				if '*OPEN70' in line:
					addwaveName=line.split("'")[1]
					print "Addwave file is: "+addwaveName
			readCard.close()

			for fn in os.listdir(cardfolder):
	    			if os.path.isfile(cardfolder+'/'+fn):
	#				if fn.startswith('addwave') or fn.startswith('ampl'):
					if fn == addwaveName or fn.startswith('ampl'):
						copyfile(cardfolder+'/'+fn,workdirTbin+'/'+fn)
			nTasks=int((float(mMax)-float(mMin))/float(binWidth)+0.00001)
			if iseed_random>0:
				iNfits_max=nseed_random 
				iNfits_min=0
		

			for iNfits in range(iNfits_min,iNfits_max):
				iNFITS=0
				if iseed_random ==  0:
					seed=seeds[iNfits]
				else:
					seed=random.randint(0,100000)
				cardName=workdirTbin+'card_'+str(iNFITS)+'_'+str(seed)+'_submit1.dat'
				if nstage==3:
					cardName=workdirTbin+'card_'+str(iNFITS)+'_'+str(seed)+'_resubmit1.dat' #The file will be copied, even if the job doesn't have to be resubmitted.
				
				copyfile(cardfolder+'/'+card,cardName)
				iwrite_wramp=0
				iread_wramp=0

#Set flags to determine what to append to the card
				if nstage == 1:
					iwrite_wramp=1

				if nstage == 0 and iNfits == 0:
					iwrite_wramp=1

				if nstage == 2:
					iread_wramp=1

				if nstage == 0 and iNfits > 0:
					iread_wramp=1

				if nstage == 3:
					iread_wramp=1


################################################### Set statements that will be appended to the card
				appendToCard=[]

				if iwrite_wramp == 1:
					appendToCard=appendToCard+["""
C
 WRAMP_WRITE_READ
C
 WRAMP_WRITE_CHECK
C
C IWRITEAMPLIT
C WRAMP_READ
C WRAMP_DELETE
C
"""]
				if iread_wramp == 1:
					appendToCard=appendToCard+["""
C
C WRAMP_WRITE_READ
C
C IWRITEAMPLIT
C
 WRAMP_READ
C
C
 WRAMP_CLOSED_WAIT
C
C WRAMP_DELETE
C
"""]


				appendToCard=appendToCard+[
	'COMPENSATE_AMP '+COMPENSATE_AMP						,
	'C'										,
	'C'										,	
	"C *OPEN70  'nmcset_"+lowerEdge+'-'+upperEdge+".dat'"				,
	'C READ  70'									,
	'C'										,
	'C - do not label file wramp with seed (will be same file for all attempts)'	,
	'C'										,
	' ISEEDAMPLIT  -1'								,
	'C'										,
	' WRAMP_CLOSED_WAIT'								,
	'C'										,
	' PARAMIN_STEP'									,
	' PARAMIN_DELETE'								,
	'C PARAMIN_NO_SUFFIX'								,
	'C'										,
	'NFITS 1'									,
	'C'										,
	"NAME_TREE_PH_IN "+pwaIn							,
	'C'										,						
	MC_char+" *PH_BINS_PREFIX '"+source+"/'"					,
	'C'										,
	"FILEWRAMP '"+wrampdir+'/wramp_'+lowerEdge+'-'+upperEdge+".dat'"		,
	'C'										,
	"DIRINTEGRALS '"+intdir+'/'+lowerEdge+'-'+upperEdge+"/'"			,
	'C'										,
	'C do not mess-up here !!!!!'							,
	'C'										,
	"*FILEFIT '"+workdirTbin+'fit_'+lowerEdge+'-'+upperEdge+".dat'"			,
	'C'										,
	"*FILEPARAM '"+workdirTbin+'param_'+lowerEdge+'-'+upperEdge+".dat'"		,
	'C'										,
	"*FILEPARAMIN '"+workdirTbin+'paramin_'+lowerEdge+'-'+upperEdge+".dat'"		,
	'C'										,
	'*INTBIN 0.500 2.500 '+lowerEdge+' '+upperEdge+' 0.010'				,
	'C'										,
	'C Please do not mess-up here  !!!!'						,
	'C*INTBIN 0.500 2.500 0.100000 1.000000 0.040'					,
	'C'										,
	' *BIN 0.500 2.500 '+lowerEdge+' '+upperEdge+' '+binWidth			,
	'C'										,
	'C -- *BIN 0.500 2.500 0.100 0.140  '+binWidth					]
###############################################################################################
				actCard=open(cardName,'a')
				for line in appendToCard:
					actCard.write(line)
					actCard.write('\n')

				logname=logdir+'/run_pwa_'+lowerEdge+'-'+upperEdge+'_'+mMin+'_'+mMax+'_'+str(seed)+'.log' 
				jobname=jobnameprefix+'_'+lowerEdge+'-'+upperEdge+'_'+mMin+'_'+mMax+'_'+str(seed)
				if not wrampmode:
					taskList='1-'+str(nTasks)
					notResubmit=[]
					if nstage == 3:				
						oldJobs=[]
						status = getRunningJobs()
						identifier = lowerEdge+'   '+upperEdge+'   '+mMin+'    '+mMax+'   '+str(seed) #Identifier has to match the lines written in the 'mappingFile'
						for line in mappingsStore:
							if identifier in line:
								oldJobs.append(line.split()[0])
						for oldJob in oldJobs:
							if status.has_key(oldJob):
								notResubmit+=status[oldJob] #Do not resubmit jobs that are still running
						for fn in os.listdir(workdirTbin):
		    					if os.path.isfile(workdirTbin+'/'+fn) and fn.startswith('param_'):
								splits=fn.split('_')
								if len(splits) > 4:
									if splits[1]== lowerEdge+'-'+upperEdge+'.dat' and splits[4]==str(seed): #Do not resubmit finished jobs
										notResubmit.append(getRightId(mMin,binWidth,splits[2]))
		#			nstage=3
					if len(notResubmit)<nTasks:
						submitCommand = 'qsub  -l short=TRUE,h_vmem=2100M -t '+taskList+' -N '+jobname+'  -j y -o '+logname+'  -wd '+workdirTbin+' ./run_pwa_new_arrays.sh '+executable+' '+cardName+' '+mMin+' '+mMax+' '+str(seed)+' '+logdir+' '+lowerEdge+' '+upperEdge+' '+binWidth
						if nstage == 3:
							submitCommand = 'qsub  -l short=TRUE,h_vmem=2100M -t '+taskList+' -N '+jobname+' -h -j y -o '+logname+'  -wd '+workdirTbin+' ./run_pwa_new_arrays.sh '+executable+' '+cardName+' '+mMin+' '+mMax+' '+str(seed)+' '+logdir+' '+lowerEdge+' '+upperEdge+' '+binWidth
						if not PRINT_CMD_ONLY:
							msg=os.popen(submitCommand).readlines()[0]		
						else:
							print submitCommand
							msg = "no_message_retrieved:_command_printed"
						print msg
						jobId=msg[15:22]
						jobIDs.append(jobId)
						if nstage == 3:
							for delId in notResubmit:
								qdelCommand = 'qdel '+jobId+' -t '+str(delId)
								if not PRINT_CMD_ONLY:
									msg=os.popen(qdelCommand).readlines()[0]
								else:
									print qdelCommand
									msg = "no_message_retrieved_command_printed"					
								print msg
							qrlsCommand = 'qrls '+jobId
							if not PRINT_CMD_ONLY:
								msg=os.popen(qrlsCommand).readlines()[0]
							else:
								print qrlsCommand
								msg = "no_message_retrieved:_command_printed"
						mappingFile.write(jobId+'   '+lowerEdge+'   '+upperEdge+'   '+mMin+'    '+mMax+'   '+str(seed)+'\n') #Has to match the identifier for resubmission
					else:
						print 'Nothing to do for: '+lowerEdge+'   '+upperEdge+'   '+mMin+'    '+mMax+'   '+str(seed)
				else:
					massBins=[]
					for i in range(0,nTasks+1):
						massBins.append(float(mMin)+i*float(binWidth))
					for i in range(len(massBins)-1):
						minStringRaw=str(massBins[i])
						maxStringRaw=str(massBins[i+1])
						minString=''
						maxString=''
						for j in range(7): # Get strings of length 7 for the mass borders
							if len(minStringRaw)>j:
								minString=minString+minStringRaw[j]
							else:
								minString=minString+'0'
							if len(maxStringRaw)>j:
								maxString=maxString+maxStringRaw[j]
							else:
								maxString=maxString+'0'
						wrampCloseString='wramp_'+lowerEdge+'-'+upperEdge+'.dat_'+minString+'_'+maxString+'_closed'
						wrampAnyString='wramp_'+lowerEdge+'-'+upperEdge+'.dat_'+minString+'_'+maxString+'*'
						if not os.path.isfile(wrampdir+'/'+wrampCloseString):
							os.popen('rm -f '+wrampAnyString) # First remove existing fles so it doesn't wait
							chunks=wrampCloseString.split('_')
							minMiss=float(chunks[2])
							missingId=getRightId(mMin,binWidth,minMiss)
							taskList=str(missingId)+'-'+str(missingId)
							submitCommand = 'qsub  -l short=TRUE,h_vmem=2100M -t '+taskList+' -N '+jobname+'  -j y -o '+logname+'  -wd '+workdirTbin+' ./run_pwa_new_arrays.sh '+executable+' '+cardName+' '+mMin+' '+mMax+' '+str(seed)+' '+logdir+' '+lowerEdge+' '+upperEdge+' '+binWidth
							if not PRINT_CMD_ONLY:
								msg=os.popen(submitCommand).readlines()[0]		
							else:
								print submitCommand
								msg = "no_message_retrieved:_command_printed"
							print msg
							time.sleep(0.1) # Not more than ten requests per second (Markus says)
		if not wrampmode:
			mappingFile.close()
		if nstage==3 and reloop:
			print 'Sleeping 20 min...'
			time.sleep(1200)
		nTasks=str(int((float(mMax)-float(mMin))/float(binWidth)+0.00001))
	return jobIDs








