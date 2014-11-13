#!/nfs/hicran/home/fkrinner/private/bin/python
from PWA import perform_PWA
import os
from sys import argv
from random import randint
import argparse

def print_perform_PWA(	card,
		name, 
		mMin, 
		mMax, 
		tBins, 
		seeds, 
		startStage, 
		maxStage, 
		proceedStages, 
		maxResubmit, 
		cleanupWramp, 
		cleanupLog, 
		cleanupFit, 
		cleanupInt, 
		intBinWidth, 
		pwaBinWidth, 
		target, 
		cardfolder, 
		intSource, 
		pwaSource, 
		cleanupCore, 
		MC_fit, 	
		treename, 
		wrampmode,
		COMPENSATE_AMP,
		PRINT_CMD_ONLY):
	print '============================================================='
	print "Confirm setting again"
	print '=======================BASIC================================='
	print "card",card
	print "name",name
	print "mMin",mMin
	print "mMax",mMax
	print "intBinWidth",intBinWidth
	print "pwaBinWidth",pwaBinWidth
	print "tBins",tBins
	print "MC_fit",MC_fit
	print '=======================SETTING==============================='
	print "seeds",seeds
	print "startStage",startStage
	print "maxStage",maxStage
	print "proceedStages",proceedStages
	print "maxResubmit",maxResubmit
	print '=======================CLEANUP==============================='
	print "cleanupWramp",cleanupWramp
	print "cleanupLog",cleanupLog
	print "cleanupFit",cleanupFit
	print "cleanupInt",cleanupInt
	print "cleanupCore",cleanupCore
	print '=======================FOLDERS==============================='
	print "target",target
	print "cardfolder",cardfolder
	print "intSource",intSource
	print "pwaSource",pwaSource
	print '=======================FLAGS================================='
	print "treename",treename
	print "wrampmode",wrampmode
	print "COMPENSATE_AMP",COMPENSATE_AMP
	print "PRINT_CMD_ONLY",PRINT_CMD_ONLY
	print '=======================CONFIRM==============================='
	if "start" == raw_input("Check settings again. Type 'start' to start the procedure: "):
		perform_PWA(	
		card,
		name, 
		mMin, 
		mMax, 
		tBins, 
		seeds, 
		startStage, 
		maxStage, 
		proceedStages, 
		maxResubmit, 
		cleanupWramp, 
		cleanupLog, 
		cleanupFit, 
		cleanupInt, 
		intBinWidth, 
		pwaBinWidth, 
		target, 
		cardfolder, 
		intSource, 
		pwaSource, 
		cleanupCore, 
		MC_fit, 	
		treename, 
		wrampmode,
		COMPENSATE_AMP = COMPENSATE_AMP,
		PRINT_CMD_ONLY = PRINT_CMD_ONLY)


parser = argparse.ArgumentParser()

parser.add_argument("name", help = "Name of the fit (card = '<cardfolder>/card_<name>.dat')")

parser.add_argument("-ncw","--noCleanupWramp",help = "Do not cleanup wramp folder",action = "store_false")
parser.add_argument("-ncl","--noCleanupLog",help = "Do not cleanup log folder",action = "store_false")
parser.add_argument("-ncf","--noCleanupFit",help = "Do not cleanup fit folder",action = "store_false")
parser.add_argument("-nci","--noCleanupIntegral",help = "Do not cleanup integral folder",action = "store_false")
parser.add_argument("-ncc","--noCleanupCore",help = "Do not cleanup core files",action = "store_false")

# StartStage 1: Submit integrals
# StartStage 2: Submit first seed for pwa (to get wramp)
# StartStage 3: Submit all other seeds for pwa
# StartStage 4: Resubmit pwa
# StartStage 5: Cleanup: Remove all log, param_, fit_, integral and wramp-files (only left with the textoutput)

parser.add_argument("-start","--startStage",type = int, help = "Stage to start with", default = 1)
parser.add_argument("-end","--maxStage",type = int, help = "Last stage to do",default = 5)
parser.add_argument("-rs","--maxResubmit",type = int, help = "Maximum number of resubmissions",default = 5)

parser.add_argument("-wramp","--wrampMode",help = "Start in wrampmode", action = "store_true")
parser.add_argument("-cmd","--PRINT_CMD_ONLY", help = "Only print sumbitcommands", action = "store_true")
parser.add_argument("-ca","--comensate_amp", help = "sets COMPENSATE_AMP 1", action = "store_true")

parser.add_argument("-tree","--treeName", type = str, help = "Name of the ROOT tree in the input file", default = None)
#treename = "'USR51mtb'" # Name for event trees, if None, the default values will be used
#treename = "'DECK_AS'"

parser.add_argument("-seed","--nSeeds", type = int, default = 9, help = "Number of random seeds for the fit")
parser.add_argument("-mMin",type = str, default = '0.500', help = "Minimum three pion mass")
parser.add_argument("-mMax",type = str, default = '2.500', help = "maximum three pion mass")
parser.add_argument("-bin" ,type = str, default = '0.040', help = "Binwidth for PWA")
parser.add_argument("-iBin",type = str, default = '0.010', help = "Integral binwidth")

parser.add_argument("-tbins", type = str, default = "second", help = "Choice of t' binning")
parser.add_argument("-is","--intSource", type = str, default = '/nfs/nas/data/compass/hadron/2008/comSkim/MC/PS-MC/trees_for_integrals/m-bins/0.100-1.000/', help = "ROOT trees for integrals")
parser.add_argument("-ps","--pwaSource", type = str, default = '/nfs/nas/data/compass/hadron/2008/comSkim/2008-binned/all/skim_2012', help = "ROOT treed to fit")
parser.add_argument("-t","--target", type = str, default =  '/nfs/mds/user/fkrinner/massIndepententFits/fits/', help = "Target directory")
parser.add_argument("-c","--cardFolder", type = str, default = '/nfs/hicran/project/compass/analysis/fkrinner/fkrinner/trunk/MassIndependentFit/cards/', help = "Directory for cards")

parser.add_argument('-mc',help = "Switches to MC fit", action = "store_true")

args = parser.parse_args()

if args.wrampMode:
	print "Using wrampmode, only do stage 2"
	args.maxStage = 2
	args.startStage = 2

if args.PRINT_CMD_ONLY:
	print "Print submit commands only. Do only one stage"
	args.maxStage = args.startStage

if args.wrampMode:
	COMPENSATE_AMP = '1'	
else:
	COMPENSATE_AMP = '0'

if args.nSeeds == 9:
	seeds=['100000', '100001','54254','27523','23411','54363','42311','43577','421341']				#	
elif  args.nSeeds == 1:
	seeds=['12345']
elif args.nSeeds == 5:
	seeds=['21899', '39718', '26029', '29007', '30856', '4566', '91819', '38734', '69235', '31436', '11226', '68076', '91814', '36147', '31110', '80205', '1952', '66030', '5555', '51640', '33799', '33219', '62791', '63431', '18401', '56213', '68951', '73530', '11025', '282', '44274', '2614', '27705', '30309', '11793', '48817', '12273', '62526', '26717', '19648', '6031', '28074', '33037', '40985', '91752', '79976', '60460', '78326', '40481', '32568']
else:
	seeds = []
	for i in range(args.nSeeds):
		seeds.append(randint(0,100000))

if args.tbins == 'four':
	tBins=[['0.10000', '0.14077'],['0.14077', '0.19435'],['0.19435', '0.32617'],['0.32617', '1.00000']]
elif args.tbins == 'first':
	tBins=[['0.10000','0.14077']]	
elif args.tbins == 'second':
	tBins=[['0.14077', '0.19435']]
elif args.tbins == 'third':
	tBins=[['0.19435', '0.32617']]	
elif args.tbins == 'fourth':
	tBins=[['0.32617', '1.00000']]	
elif args.tbins == 'flo':
	tBins = [['0.100000','0.112853'],['0.112853','0.127471'],['0.127471','0.144385'],['0.144385','0.164401'],['0.164401','0.188816'],['0.188816','0.219907'],['0.219907','0.262177'],['0.262177','0.326380'],['0.326380','0.448588'],['0.448588','0.724294'],['0.724294','1.000000']]
elif args.tbins == 'uhl':
	tBins=[['0.100000', '0.116349',],['0.116349', '0.135550'],['0.135550', '0.158754'],['0.158754', '0.187960'],['0.187960', '0.227078'],['0.227078', '0.285410'],['0.285410', '0.394889'],['0.394889', '1.000000']]
else:
	print "Unknown t'-binning. Exit."
	exit(1)

if os.path.isfile(args.cardFolder+'/card_'+args.name+'.dat'):
	card='card_'+args.name+'.dat'
else:
	print "Card '",card,"' does not exist. Exit."
	exit(1)	

print "Startstage: "+str(args.startStage)
raw_input()
print "MaxStage: "+str(args.maxStage)
raw_input()
print "Cleanup:"
print "Wramp\tLog\tFit\tInt\tCore"
print str(args.noCleanupWramp)+'\t'+str(args.noCleanupLog)+'\t'+str(args.noCleanupFit)+'\t'+str(args.noCleanupIntegral)+'\t'+str(args.noCleanupCore)
print
print "mMin\tmMax\tbinWidth"
print args.mMin+'\t'+args.mMax+'\t'+args.bin
print "tBins:"
print tBins
print "seeds:"
print seeds
print "card:"
print card
if not COMPENSATE_AMP == '0':
	print "Using: COMPENSATE AMP "+COMPENSATE_AMP

if args.mc:
	mcconf = 'mc'
	conf = raw_input("Fit to MC data. Confirm with 'mc'")
else:
	mcconf = 'no'
	conf = raw_input("Fit to real data. Confirm with 'no'")
if not mcconf == conf: # Put his here to not accidentally submit wrong data
	print "MC status not confirmed, Exit."
	exit(1)


if args.wrampMode:
	print "Starting in wrampmode"
	answ = raw_input("Confirm with 'yes'?")
	if not answ == 'yes':
		print "Wrampmode not confirmed. Exit."
		exit(1)

print '============================================================='
confirm = raw_input("Are these settings correct?")
if not confirm =='yes':
	exit(1)
print_perform_PWA(	card,
		args.name, 
		args.mMin, 
		args.mMax, 
		tBins, 
		seeds, 
		args.startStage, 
		args.maxStage, 
		True, 
		args.maxResubmit, 
		args.noCleanupWramp, 
		args.noCleanupLog, 
		args.noCleanupFit, 
		args.noCleanupIntegral, 
		args.iBin, 
		args.bin, 
		args.target, 
		args.cardFolder, 
		args.intSource, 
		args.pwaSource, 
		args.noCleanupCore, 
		args.mc, 	
		args.treeName, 
		wrampmode=args.wrampMode, 
		COMPENSATE_AMP = COMPENSATE_AMP, 
		PRINT_CMD_ONLY = args.PRINT_CMD_ONLY
								)

