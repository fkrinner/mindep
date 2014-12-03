#!/nfs/hicran/home/fkrinner/private/bin/python
import sys
from sys import argv
from sys import exit
import time
import os
import call_submit_integrals_fabi
from call_submit_integrals_fabi import submit_integrals
import call_submit_pwa_fabi
from call_submit_pwa_fabi import submit_pwa
import shutil
import datetime
def writte(fil,outstring):
	""" Print a string and write it to a file"""
	print outstring
	fil.write(outstring)
def eksit(i):
	"""Exit method, can kill the mother-process, if wanted (Fire and forget)"""
#	ppid=os.getppid()
#	os.popen("kill -9 "+str(ppid)) # Use this to kill also the shell, where the script is running
	exit(0)

def perform_PWA(card,			# Name of the card
		name,			# Name of the fit
		mMin,			# Lower mass Limit
		mMax,			# Upper mass Limit
		tBins,			# t' bins
		seeds,			# seeds
		startStage,		# Stage to start at
		maxStage,		# Final Stage
		proceedStages,		# Flag to proceed after stages
		maxResubmit,		# Number of maximum resubmits
		cleanupWramp,		# Clean
		cleanupLog,		#	up
		cleanupFit,		#
		cleanupInt,		#		flags
		intBinWidth,		# Bin width for integrals
		pwaBinWidth,		# Bin width for PWA
		target,			# Target folder
		cardfolder,		# Folder with card
		intSource,		# Source for integrals
		pwaSource,		# Source for PWA (events)
		cleanupCore = True,	# Cleanupt core files
		MC_Fit = False,		# Flag if fit to MC events
		treename = None,	# Gives the name of the ROOT tree in thr input files Standard name, if none
		wrampmode = False,	# Wrampmode, only used, if wramp-files are inclomplete. 
		COMPENSATE_AMP	= '0',	# Compensate_amp flag in the card
		PRINT_CMD_ONLY = False	# Flag to print submit commends rather than executing them
							):
	"""Main method to perform a PWA on the E18 batch system"""
	KILL_TO_WIN = True # Kill first seed after completing the wramp file to start the other seeds earlier
	if len(seeds) == 1:
		KILL_TO_WIN = False

	#Set the directories
	logDir=target+'/'+name+'/log'
	intDir=target+'/'+name+'/integrals'
	fitDir=target+'/'+name+'/fit'	
	wrampDir=target+'/'+name+'/wramp'
	if not os.path.isdir(target+'/'+name):
		os.makedirs(target+'/'+name)
	if not os.path.isdir(wrampDir):
		os.makedirs(wrampDir)

	#Set up the log file
	totalLog=open(target+'/'+name+'/log_pwa_'+name+'.log','w')
	writte(totalLog,'Start complete PWA process\n')
	writte(totalLog,'Target: '+target+'\nCard: '+cardfolder+'/'+card+'\nm3Pi: '+mMin+'-'+mMax+'\nIntegral bidwidth: '+intBinWidth+'\nPWA binwidth: '+pwaBinWidth+"\nt': "+str(tBins)+'\nIntegral Source: '+intSource+'\nPWA source: '+pwaSource+'\n\nStart at stage: '+str(startStage)+'\n')

	#Determine mode from card
	card_open = open(cardfolder+'/'+card,'r')
	for line in card_open.readlines():
		if 'CARD_FOR_MONTE_CARLO' in line:
			MC_Fit = True
			writte(totalLog,"Fit to MC_data")
	card_open.close()

	stage=startStage

	#Stage 1: Calculate integrals
	if stage == 1:
		writte(totalLog,'--------------------------------------------------------------------------------\n')
		writte(totalLog,'Stage 1: Submit integrals.\n')
		writte(totalLog,'--------------------------------------------------------------------------------\n')
		writte(totalLog,'   '+str(datetime.datetime.now())+'\n')
		expectedFiles=int((float(mMax)-float(mMin))/float(intBinWidth)+0.00001) #Calculate number of expaected integral files
		writte(totalLog,'   Expect '+str(expectedFiles)+' integral files.\n')
		jobIDs=submit_integrals(intDir,intSource,logDir,cardfolder,card,mMin,mMax,intBinWidth,tBins, MC_Fit,COMPENSATE_AMP=COMPENSATE_AMP,PRINT_CMD_ONLY=PRINT_CMD_ONLY) #Submit jobs
		writte(totalLog,'   Wait for cluster to finish.\n')
		while True: #Wait until all integral jobs are finished
			writte(totalLog,'   Sleep: '+str(datetime.datetime.now())+'\n')
			time.sleep(300)	
			stat=os.popen('qstat').readlines()
			nRun = 0
			for line in stat:
				for ID in jobIDs:
					if ID in line:
						nRun+=1
			print '   ',nRun,' jobs still running'
			if nRun==0:
				break
		writte(totalLog,'   Cluster has finished the integral-jobs.\n')
		writte(totalLog,'   Check, if all integral files have been created.\n')
		for tBin in tBins: #Check if all integral files exist
			actFolder=intDir+'/'+tBin[0]+'-'+tBin[1]	

			NdiagNacc=0
			NdiagAcc=0
			DiagNacc=0
			DiagAcc=0
			TxtAcc=0
			TxtNacc=0
			for fn in os.listdir(actFolder):
				if '_nondiag.dat' in fn:
					NdiagNacc+=1
				if '_nondiag_acc.dat' in fn:
					NdiagAcc+=1
				if '_diag_acc.dat' in fn:
					DiagAcc+=1
				if '_diag.dat' in fn:
					DiagNacc+=1
				if 'PWANormIntegralsAcc_' in fn:
					TxtAcc+=1
				if 'PWANormIntegralsNAcc_' in fn:
					TxtNacc+=1
			writte(totalLog,"   Found the following integral files:\nNdiagNacc\tNdiagAcc\tDiagAcc\t\tDiagNacc\tTxtAcc\t\tTxtNacc\n"+str(NdiagNacc)+'\t\t'+str(NdiagAcc)+'\t\t'+str(DiagAcc)+'\t\t'+str(DiagNacc)+'\t\t'+str(TxtAcc)+'\t\t'+str(TxtNacc)+'\n')
			if NdiagNacc == expectedFiles and NdiagAcc == expectedFiles and DiagAcc == expectedFiles and DiagNacc == expectedFiles and TxtAcc == expectedFiles and TxtNacc == expectedFiles:
				writte(totalLog,"   All integral files found for: t'="+str(tBin)+'\n\n')
			else:
				writte(totalLog,"Not all integral files found for t'="+str(tBin)+'. Exit.')
				writte(totalLog,'   '+str(datetime.datetime.now())+'\n')
				totalLog.close()
				eksit(1)
		if proceedStages and stage < maxStage:
			stage=2
		writte(totalLog,'Stage 1 successful. All integral files found.\n\n')

	#Stage 2: Create wramp files
	if stage==2:
		writte(totalLog,'--------------------------------------------------------------------------------\n')
		writte(totalLog,'Stage 2: First seeds for wramp files.\n')
		writte(totalLog,'--------------------------------------------------------------------------------\n')
		writte(totalLog,'   '+str(datetime.datetime.now())+'\n')
		expectedFiles=int((float(mMax)-float(mMin))/float(pwaBinWidth)+0.00001)*len(tBins)
		writte(totalLog,'   Expect '+str(expectedFiles)+' wramp files.\n')
		jobIDs=submit_pwa(fitDir,intDir,pwaSource,logDir,wrampDir,cardfolder,card,mMin,mMax,pwaBinWidth,1,tBins,seeds,mappingName='map',MC_Fit=MC_Fit,treename=treename,wrampmode=wrampmode,COMPENSATE_AMP=COMPENSATE_AMP,PRINT_CMD_ONLY=PRINT_CMD_ONLY) #Submit jobs
		writte(totalLog,'   Wait for cluster to finish.\n')
		while True: #Wait for jobs
			time.sleep(300)	
			writte(totalLog,'   Sleep: '+str(datetime.datetime.now())+'\n')
			if KILL_TO_WIN:
				nClosed=0
				nWramp=0
				for fn in os.listdir(wrampDir):
					if 'wramp_' in fn:
						nWramp+=1
					if '_closed' in fn:
						nClosed+=1
				if nClosed == expectedFiles and not nWramp < 3*expectedFiles:
					for iidd in jobIDs:
						writte(totalLog,'   Killing job '+iidd+' because all wramp files exist, so all SEEDS can run.\n')
						os.popen('qdel '+iidd)
					break
			nRun = 0
			stat=os.popen('qstat').readlines()
			for line in stat:
				for ID in jobIDs:
					if ID in line:
						nRun+=1
			print '   ',nRun,' jobs still running'
			if nRun==0:
				break
		writte(totalLog,'   Cluster has finished the PWA-jobs.\n')
		for i in range(3):
			writte(totalLog,'   Check, if all wramp files have been created.\n')
			nClosed=0
			nWramp=0
			for fn in os.listdir(wrampDir): #Check if all wramp files exist
				if 'wramp_' in fn:
					nWramp+=1
				if '_closed' in fn:
					nClosed+=1
			writte(totalLog,'   Found '+ str(nWramp)+" 'wramp'-files "+ str(nClosed) +' are closed.\n')
			wrampDone = False
			if nClosed == expectedFiles and not nWramp < 3*expectedFiles:
				writte(totalLog,"   All 'wramp' files found.\n")
				wrampDone = True
				break 
			else:
				writte(totalLog,"   Not all 'wramp' files found. Resubmitting in wrampmode. #"+str(i)+"\n")
				jobIDs=submit_pwa(fitDir,intDir,pwaSource,logDir,wrampDir,cardfolder,card,mMin,mMax,pwaBinWidth,1,tBins,seeds,mappingName='map',MC_Fit=MC_Fit,treename=treename,wrampmode=True,COMPENSATE_AMP=COMPENSATE_AMP,PRINT_CMD_ONLY=PRINT_CMD_ONLY) #Submit jobs
				while True:
					time.sleep(300)	
					writte(totalLog,'   Sleep: '+str(datetime.datetime.now())+'\n')
					nRun = 0
					stat=os.popen('qstat').readlines()
					for line in stat:
						for ID in jobIDs:
							if ID in line:
								nRun+=1
					print '   ',nRun,' jobs still running'
					if nRun==0:
						break
		if not wrampDone:
			writte(totalLog,"Not all 'wramp' files. Exit.")
			writte(totalLog,'   '+str(datetime.datetime.now())+'\n')
			totalLog.close()
			eksit(1)
		if proceedStages and stage < maxStage:
			stage=3
		writte(totalLog,"Stage 2 successful. All 'wramp' files found\n\n")


	if stage ==3 and (len(seeds)>1 or KILL_TO_WIN): # Submit additional seeds
		writte(totalLog,'--------------------------------------------------------------------------------\n')
		writte(totalLog,'Stage 3: Submit additional seeds.\n')
		writte(totalLog,'--------------------------------------------------------------------------------\n')
		writte(totalLog,'   '+str(datetime.datetime.now())+'\n')
		if KILL_TO_WIN:
			adsed = seeds[:]
			adsed.insert(0,'000000') # put a dummy seed to the front, that will not be submitted by stage 2, to run also the first real seed, which was killed after completing the wramp file.
			jobIDs=submit_pwa(fitDir,intDir,pwaSource,logDir,wrampDir,cardfolder,card,mMin,mMax,pwaBinWidth,2,tBins,adsed,mappingName='map',MC_Fit=MC_Fit,treename=treename,PRINT_CMD_ONLY=PRINT_CMD_ONLY)
		else:
			jobIDs=submit_pwa(fitDir,intDir,pwaSource,logDir,wrampDir,cardfolder,card,mMin,mMax,pwaBinWidth,2,tBins,seeds,mappingName='map',MC_Fit=MC_Fit,treename=treename,COMPENSATE_AMP=COMPENSATE_AMP,PRINT_CMD_ONLY=PRINT_CMD_ONLY)
		writte(totalLog,'   Wait for cluster to finish.\n')
		while True:
			time.sleep(300)	
			writte(totalLog,'   Sleep: '+str(datetime.datetime.now())+'\n')
			stat=os.popen('qstat').readlines()
			nRun = 0
			for line in stat:
				for ID in jobIDs:
					if ID in line:
						nRun+=1
			print '   ',nRun,' jobs still running'
			if nRun==0:
				break
		writte(totalLog,'   Cluster has finished the PWA-jobs.\n\n')
		if proceedStages:
			stage=4
		writte(totalLog,'Stage 3 finished.\n\n')
	elif stage==3 and len(seeds) == 1:
		writte(totalLog,'--------------------------------------------------------------------------------\n')
		writte(totalLog,"Skip stage 3, no additional seeds.\n")
		writte(totalLog,'--------------------------------------------------------------------------------\n')
		writte(totalLog,'   '+str(datetime.datetime.now())+'\n\n')
		if proceedStages and stage < maxStage:
			stage=4
		writte(totalLog,'Stage 3 finished.\n\n')

	allParam_=False
	if stage==4:
		writte(totalLog,'--------------------------------------------------------------------------------\n')
		writte(totalLog,'Stage 4: Resubmit unfinished jobs.\n')
		writte(totalLog,'--------------------------------------------------------------------------------\n')
		writte(totalLog,'   '+str(datetime.datetime.now())+'\n')
		expectedFiles=int((float(mMax)-float(mMin))/float(pwaBinWidth)+0.00001)*len(seeds)
		writte(totalLog,"   Expect "+str(expectedFiles)+" files in each t' bin.\n")
		allParam_=False #All parameter files exist
		for i in range(maxResubmit): #Loop over maximum number of resubmissions
			nParam_=0
			writte(totalLog,'   Resubmission '+str(i+1)+'.\n')
			writte(totalLog,"   Check if some 'param_...' files are missing.\n")
			for tBin in tBins:
				nMom=0
				actFolder = fitDir+'/'+tBin[0]+'-'+tBin[1]+'/'
				for fn in os.listdir(actFolder):
					if 'param_' in fn:
						nMom+=1
						nParam_+=1
				writte(totalLog,'   Found '+str(nMom)+" 'param_...' files for t'="+str(tBin)+'\n')		
			if nParam_ < len(tBins) * expectedFiles:
				writte(totalLog,"   Some 'param_...' files missing. Resubmit.\n")
				jobIDs=submit_pwa(fitDir,intDir,pwaSource,logDir,wrampDir,cardfolder,card,mMin,mMax,pwaBinWidth,3,tBins,seeds,mappingName='map',MC_Fit=MC_Fit,treename=treename,COMPENSATE_AMP=COMPENSATE_AMP,PRINT_CMD_ONLY=PRINT_CMD_ONLY)
				writte(totalLog,'   Wait for cluster to finish.\n')
				while True:
					time.sleep(300)	
					writte(totalLog,'   Sleep: '+str(datetime.datetime.now())+'\n')
					stat=os.popen('qstat').readlines()
					nRun = 0
					for line in stat:
						for ID in jobIDs:
							if ID in line:
								nRun+=1
					print '   ',nRun,' jobs still running'
					if nRun==0:
						break
				writte(totalLog,'   Cluster has finished the PWA-jobs.\n\n')
			else: # Break if all parameter files exist
				allParam_=True
				writte(totalLog,"   All 'param_...' files found. Nothing to be done in stage 4.\n")
				break
		if not allParam_:
			nParam_=0
			for tBin in tBins: #Check again, if the last resubmission did the job
				nMom=0
				actFolder = fitDir+'/'+tBin[0]+'-'+tBin[1]+'/'
				for fn in os.listdir(actFolder):
					if 'param_' in fn:
						nMom+=1
						nParam_+=1
				writte(totalLog,'   Found '+str(nMom)+" 'param_...' files for t'="+str(tBin)+'\n')		
			if nParam_ < len(tBins) * expectedFiles:
				writte(totalLog,"   Some 'param_...' files missing. Reached maximum number of resubmissions. End.\n")
				writte(totalLog,'   '+str(datetime.datetime.now())+'\n')
				totalLog.close()
				exit(1)
			else:
				allParam_=True
				writte(totalLog,"   All 'param_...' files found. Nothing to be done in stage 4.\n")
		if allParam_:
			writte(totalLog,"Stage 4 successful. All 'param_...' files found.\n\n")
			if proceedStages and stage<maxStage:
				stage=5


	if stage==5: #Delete not needed files
		writte(totalLog,'--------------------------------------------------------------------------------\n')
		writte(totalLog,'Stage 5: Cleanup.\n')
		writte(totalLog,'--------------------------------------------------------------------------------\n')
		writte(totalLog,'   '+str(datetime.datetime.now())+'\n')
		if cleanupWramp:
			writte(totalLog,"   Delete wrampdir\n")
			shutil.rmtree(wrampDir)
		if cleanupLog:
			writte(totalLog,"   Delete logdir\n")
			shutil.rmtree(logDir)
		if cleanupFit:
			writte(totalLog,"   Delete fitdir except for textoutput\n")
			for tBin in tBins:
				sfits=0
				actFolder=fitDir+'/'+tBin[0]+'-'+tBin[1]
				for fn in os.listdir(actFolder):
					if not 'text' in fn:
						if 'param' in fn or 'fit' in fn and not 'sfit' in fn:
							os.remove(actFolder+'/'+fn)
					if 'sfit' in fn and sfits>0:
						os.remove(actFolder+'/'+fn)
					else:
						sfits+=1					
		if cleanupCore:
			writte(totalLog,"   Delete core files\n")
			for tBin in tBins:
				actFolder=fitDir+'/'+tBin[0]+'-'+tBin[1]
				for fn in os.listdir(actFolder):
					if 'core' in fn:
						os.remove(actFolder+'/'+fn)
		if cleanupInt:
			writte(totalLog,"   Delete integral files except for textoutput\n")
			for tBin in tBins:
				actFolder=intDir+'/'+tBin[0]+'-'+tBin[1]		
				for fn in os.listdir(actFolder):
					if '_nondiag.dat' in fn or '_nondiag_acc.dat' in fn or '_diag.dat' in fn or '_diag_acc.dat' in fn:
						os.remove(actFolder+'/'+fn)
		writte(totalLog,'   Cleanup complete\n')
		writte(totalLog,"Stage 5 successful.\n\n")

	writte(totalLog,'\n\n--------------------------------------------------------------------------------\nAll done.\nEnd.')
	writte(totalLog,'   '+str(datetime.datetime.now())+'\n')
	totalLog.close()
	eksit(0)





