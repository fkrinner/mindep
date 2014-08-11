import os
import shutil
import random
from shutil import copyfile
"""
Submits the integrator to the e18 cluster
"""
def submit_integrals(target,source,logdir,cardFolder,card,mMin,mMax,binWidth,tBins, is_MC):
#	executable='/nfs/hicran/project/compass/analysis/fkrinner/workDir/compassPWAbin_new/bin/integrator_3pic_compass_2008florian3_dfunc.static'
	executable='/nfs/hicran/project/compass/analysis/fkrinner/workDir/compassPWAbin_big/bin/integrator_3pic_compass_2008florian3_dfunc.static'
	jobIDs=[]
	if not os.path.exists(logdir):
		os.makedirs(logdir)
	for tBin in tBins:
		lowerEdge=tBin[0]
		upperEdge=tBin[1]
		workdirTbin=target+'/'+lowerEdge+'-'+upperEdge
		if not os.path.exists(workdirTbin):
			os.makedirs(workdirTbin)
		copyfile(cardFolder+'/'+card,workdirTbin+'/card.dat')
		cardFile=open(workdirTbin+'/card.dat','a')
		appendToCard=[
"INT_TEXT_OUTPUT  1"                                            ,
"COMPENSATE_AMP    0"						,
"NAME_TREE_MC_IN  'USR51MCout'"					,
"TYPE_TREE_MC_IN  1"						,
"*MC_BINS_PREFIX '"+source+"'"					,
"*MC_BINS_SUFFIX '.root'"					,
"NMC1 1000000"							,
"DIRINTEGRALS  '"+target+"/"+lowerEdge+"-"+upperEdge+"/'"	,
"*INTBIN  0.500  2.500  "+lowerEdge+"  "+upperEdge+"  0.010"	]
		for line in appendToCard:
			cardFile.write(line+'\n')
		if is_MC:
			cardFile.write("NO_ACC\n")
		cardFile.close()
		readCard=open(cardFolder+'/'+card,'r')
		for line in readCard.readlines():
			if '*OPEN70' in line:
				addwaveName=line.split("'")[1]
				print "Addwave file is: "+addwaveName
		readCard.close()
		for fn in os.listdir(cardFolder):
    			if os.path.isfile(cardFolder+'/'+fn):
				if fn == addwaveName or fn.startswith('ampl'):
					copyfile(cardFolder+'/'+fn,workdirTbin+'/'+fn)	
		seed=str(random.randint(0,100000))	
		nTasks=str(int((float(mMax)-float(mMin))/float(binWidth)+0.00001))			
		submitCommand="qsub  -l short=TRUE,h_vmem=1100M -l hostname=!short_opteron@node2.cluster -t 1-"+nTasks+" -j y -o "+logdir+"/run_integrator_"+lowerEdge+"-"+upperEdge+".log  -wd "+target+"/"+lowerEdge+"-"+upperEdge+" ./run_integrator_array.sh "+executable+" "+target+"/"+lowerEdge+"-"+upperEdge+"/card.dat "+seed+" "+logdir+" "+lowerEdge+" "+upperEdge+" "+mMin+" "+mMax+" "+binWidth
#		print submitCommand
		msg=os.popen(submitCommand).readlines()[0]		
		print msg
		jobIDs.append(msg[15:22])
	return jobIDs
