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
cleanupCore=True	# Will delete all core dump files

wrampmode = False

COMPENSATE_AMP = '0'
#COMPENSATE_AMP = '1'

try:
	name=argv[1] # Name for the fit to create the folder. Will use the card './cards/card_<name>.dat
except:
	name=raw_input("Give a name for the fit: ")

#treename = "'USR51mtb'" # Name for event trees, if None, the default values will be used
#treename = "'DECK_AS'"

# StartStage 1: Submit integrals
# StartStage 2: Submit first seed for pwa (to get wramp)
# StartStage 3: Submit all other seeds for pwa
# StartStage 4: Resubmit pwa
# StartStage 5: Cleanup: Remove all log, param_, fit_, integral and wramp-files (only left with the textoutput)

#--------------------------- Define the fit --------------------------------------------------------------------#
seeds=['100000', '100001','54254','27523','23411','54363','42311','43577','421341']				#	
#seeds=['12345']												#
#seeds=['21899', '39718', '26029', '29007', '30856', '4566', '91819', '38734', '69235', '31436', '11226', '68076', '91814', '36147', '31110', '80205', '1952', '66030', '5555', '51640', '33799', '33219', '62791', '63431', '18401', '56213', '68951', '73530', '11025', '282', '44274', '2614', '27705', '30309', '11793', '48817', '12273', '62526', '26717', '19648', '6031', '28074', '33037', '40985', '91752', '79976', '60460', '78326', '40481', '32568']													#
														#
														#
target='/nfs/mds/user/fkrinner/massIndepententFits/fits/'							# Target folder for results
cardfolder='/nfs/hicran/project/compass/analysis/fkrinner/fkrinner/trunk/MassIndependentFit/cards/'		# Folder for the cards
#card='card_test0.dat'												#					
if os.path.isfile(cardfolder+'/card_'+name+'.dat'):								# Use <cardfolder>/card_<name>.dat	
	card='card_'+name+'.dat'										#
else:														#
	print "Card does not exist"										#
	exit(1)													#
#mMin='0.500'													# Mass Limits (Given as Strings)
#mMax='2.500'													#
mMax='1.540'													#
mMin='1.500'													#
#mMax='1.260'													#
														#
intBinWidth='0.010'												# Bin widths (As Strings)
pwaBinWidth='0.040'												#
#pwaBinWidth = '0.020'														#
														#
#tBins=[['0.10000','0.14077']]											# t' Bins as pairs of strings
#tBins=[['0.10000', '0.14077'],['0.14077', '0.19435'],['0.19435', '0.32617'],['0.32617', '1.00000']]		#
#tBins=[['0.10000', '0.14077'],['0.14077', '0.19435']]								#
#tBins=[['0.32617', '1.00000']]											#
tBins=[['0.14077', '0.19435']]											#
#tBins=[['0.10000', '0.14077']]											#
#tBins=[['0.112853','0.127471']]										#				
#tBins=[['0.164401','0.188816']]										#
														#
#Flo's eleven													#
#tBins = [['0.100000','0.112853'],['0.112853','0.127471'],['0.127471','0.144385'],['0.144385','0.164401'],['0.164401','0.188816'],['0.188816','0.219907'],['0.219907','0.262177'],['0.262177','0.326380'],['0.326380','0.448588'],['0.448588','0.724294'],['0.724294','1.000000']]
														#
#Sebastian's eight												#
#tBins=[['0.100000', '0.116349',],['0.116349', '0.135550'],['0.135550', '0.158754'],['0.158754', '0.187960'],['0.187960', '0.227078'],['0.227078', '0.285410'],['0.285410', '0.394889'],['0.394889', '1.000000']]
														#
														#
intSource='/nfs/nas/data/compass/hadron/2008/comSkim/MC/PS-MC/trees_for_integrals/m-bins/0.100-1.000/'		# Phase Space Monte Carlo for Integrals
pwaSource='/nfs/nas/data/compass/hadron/2008/comSkim/2008-binned/all/skim_2012'					#  3 Pi Data
#pwaSource='/nfs/nas/data/compass/hadron/2008/comSkim/MC/DECK/18082011/m-bins/'					#  Deck MC (Dima's model)
#pwaSource='/nfs/nas/data/compass/hadron/2008/comSkim/MC/DECK/19122011/t-m-bins/'				#  Other Deck model
#---------------------------------------------------------------------------------------------------------------#
print "Startstage: "+str(startStage)
raw_input()
print "MaxStage: "+str(maxStage)
raw_input()
print "Cleanup:"
print "Wramp\tLog\tFit\tInt\tCore"
print str(cleanupWramp)+'\t'+str(cleanupLog)+'\t'+str(cleanupFit)+'\t'+str(cleanupInt)+'\t'+str(cleanupCore)
print
print "mMin\tmMax\tbinWidth"
print mMin+'\t'+mMax+'\t'+pwaBinWidth
print "tBins:"
print tBins
print "seeds:"
print seeds
print "card:"
print card
if not COMPENSATE_AMP == '0':
	print "Using: COMPENSATE AMP "+COMPENSATE_AMP

mcfit = raw_input("MC_fit?:")
if mcfit.lower() == 'y':
	MC_fit = True
elif mcfit.lower()=='n':
	MC_fit = False
else:
	print "++++++++++++++++!!!!!!!!!!!!!!!!!!"
	print "not determined whether MC fit or not"
	print "eksit(1) lololo"
	exit(1)


if MC_fit:
	print "Fit to MC data !!1"
else:
	print "Fit to real data!!"
try:
	if treename:
		print "Using fixed treename for events:",treename
except NameError:
	treename = None
if wrampmode:
	print "Starting in wrampmode"
	answ = raw_input("Confirm?")
	if not answ == 'yes':
		exit(1)

print '__________________________-__________________________________'
confirm = raw_input("Are these settings correct?")
if not confirm =='yes':
	exit(1)
perform_PWA(card,name,mMin,mMax,tBins,seeds,startStage,maxStage,proceedStages,maxResubmit,cleanupWramp,cleanupLog,cleanupFit,cleanupInt,intBinWidth,pwaBinWidth,target,cardfolder,intSource,pwaSource,cleanupCore,MC_fit,treename,wrampmode=wrampmode, COMPENSATE_AMP = COMPENSATE_AMP)

