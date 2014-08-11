import os

def getQstat():
	qstat = os.popen('qstat').readlines()
	return qstat


def getRunningJobs(qstatIn=[]):
	jobs = {}
	if qstatIn==[]:
		qstat = getQstat()
	else:
		qstat=qstatIn
	for i in range(2,len(qstat)):
		chunks 	= qstat[i].split()
		jobId 	= chunks[0]
		priority= float(chunks[1])
		name 	= chunks[2]
		user 	= chunks[3]
		state	= chunks[4]
		date	= chunks[5]
		time	= chunks[6]	
		jobIds	= chunks[-1]
#		print jobIds
		splitIds1= jobIds.split(',') 
		jobsRun=[]
		for idString in splitIds1:
			splitIds=idString.split(':')
			if len(splitIds)==1:
				jobsRun.append(int(splitIds[0]))
			else:
				limits=splitIds[0].split('-')
				lower=int(limits[0])
				upper=int(limits[1])
				stepSize=int(splitIds[1])
				actJob=lower
				while actJob <= upper:
					jobsRun.append(actJob)
					actJob+=stepSize
		if jobs.has_key(jobId):
			jobs[jobId]=jobs[jobId]+jobsRun
		else:
			jobs[jobId]=jobsRun
		jobs[jobId].sort()
	return jobs


