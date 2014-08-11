#!/nfs/hicran/home/fkrinner/private/bin/python
from PWA import perform_PWA
import os
from sys import argv

startStage=1
maxStage=5
proceedStages=True
maxResubmit=5



cleanupWramp=True	# Will delete the wramp-folder after completing the fit.
cleanupLog=True		# Will delete the log-folder after completing the fit
cleanupFit=True		# Will delete all 'param_', 'paramin_', 'fit_', 'sfit_' files after completing the fit. Only textoutput left.
cleanupInt=True		# Will delete all Integral-files after completing the fit. Only textoutput left.
cleanupCore=True

MC_fit = True



try:
	name=argv[1]
except:
	name=raw_input("Give a name for the fit: ")



# StartStage 1: Submit integrals
# StartStage 2: Submit first seed for pwa (to get wramp)
# StartStage 3: Submit all other seeds for pwa
# StartStage 4: Resubmit pwa
# StartStage 5: Cleanup: Remove all log, param_, fit_, integral and wramp-files (only left with the textoutput)

#--------------------------- Define the fit --------------------------------------------------------------------#
#seeds=['100000', '100001','54254','27523','23411','54363','42311','43577','421341']				#	
#seeds=['12345']												#
seeds=['21899', '39718', '26029', '29007', '30856', '4566', '91819', '38734', '69235', '31436', '11226', '68076', '91814', '36147', '31110', '80205', '1952', '66030', '5555', '51640', '33799', '33219', '62791', '63431', '18401', '56213', '68951', '73530', '11025', '282', '44274', '2614', '27705', '30309', '11793', '48817', '12273', '62526', '26717', '19648', '6031', '28074', '33037', '40985', '91752', '79976', '60460', '78326', '40481', '32568']									#
														#
														#
target='/nfs/mds/user/fkrinner/massIndepententFits/fits/'							#
cardfolder='/nfs/hicran/project/compass/analysis/fkrinner/fkrinner/trunk/MassIndependentFit/cards/'		#
#card='card_test0.dat'												#					
if os.path.isfile(cardfolder+'/card_'+name+'.dat'):								#	
	card='card_'+name+'.dat'										#
else:														#
	print "Card does not exist"										#
	exit(1)													#
#mMin='0.500'													#
#mMax='2.500'													#
mMax='1.540'													#
mMin='1.500'													#
#mMax='1.260'													#
														#
intBinWidth='0.010'												#
pwaBinWidth='0.040'												#
														#
#tBins=[['0.10000','0.14077']]											#
#tBins=[['0.10000', '0.14077'],['0.14077', '0.19435'],['0.19435', '0.32617'],['0.32617', '1.00000']]		#
#tBins=[['0.32617', '1.00000']]											#
tBins=[['0.14077', '0.19435']]											#
#tBins=[['0.112853','0.127471']]										#				
														#
														#
intSource='/nfs/nas/data/compass/hadron/2008/comSkim/MC/PS-MC/trees_for_integrals/m-bins/0.100-1.000/'		#
pwaSource='/nfs/nas/data/compass/hadron/2008/comSkim/2008-binned/all/skim_2012'					#
#---------------------------------------------------------------------------------------------------------------#
print "Startstage: "+str(startStage)
raw_input()
print "MaxStage: "+str(maxStage)
raw_input()
print "Cleanup:"
print "Wramp\tLog\tFit\tInt\tCore"
print str(cleanupWramp)+'\t'+str(cleanupLog)+'\t'+str(cleanupFit)+'\t'+str(cleanupInt)+'\t'+str(cleanupCore)
print
print "mMin\tmMax"
print mMin+'\t'+mMax
print "tBins:"
print tBins
print "seeds:"
print seeds
print "card:"
print card
if MC_fit:
	print "Fit to MC data !!1"
else:
	print "Fit to real data!!"
print '__________________________-__________________________________'
confirm = raw_input("Are these settings correct?")
if not confirm =='yes':
	exit(1)
perform_PWA(card,name,mMin,mMax,tBins,seeds,startStage,maxStage,proceedStages,maxResubmit,cleanupWramp,cleanupLog,cleanupFit,cleanupInt,intBinWidth,pwaBinWidth,target,cardfolder,intSource,pwaSource,cleanupCore,MC_fit)

