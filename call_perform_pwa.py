from PWA import perform_PWA
from sys import argv

name = argv[1]

# Crucial definitions
card = 'card_'+name+'.dat'
mMin = '1.50'
mMax = '1.54'
tBins=[['0.14077', '0.19435']]
seeds=['100000', '100001','54254','27523','23411','54363','42311','43577','421341']


# More definitions
startStage=1
maxStage=5
proceedStages=True
maxResubmit=5
cleanupWramp=True
cleanupLog=True
cleanupFit=True
cleanupInt=True
cleanupCore=True

intSource='/nfs/nas/data/compass/hadron/2008/comSkim/MC/PS-MC/trees_for_integrals/m-bins/0.100-1.000/'
pwaSource='/nfs/nas/data/compass/hadron/2008/comSkim/2008-binned/all/skim_2012'	
target='/nfs/mds/user/fkrinner/massIndepententFits/fits/'
cardfolder='/nfs/hicran/project/compass/analysis/fkrinner/fkrinner/trunk/MassIndependentFit/cards/'

intBinWidth='0.010'
pwaBinWidth='0.040'

perform_PWA(	card,			# Name of the card
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
		intSource,
		pwaSource,
		cleanupCore
					)

