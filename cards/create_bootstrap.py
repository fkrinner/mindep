#!/nfs/hicran/home/fkrinner/private/bin/python
import sys
from sys import argv

# modes:'b': bootstrapped isobar, 'i': normal isobar, 'd': de-isobarred, '0' not used

bootstrapped = ["rho1pp0pS","rho2pp1pD","f01pp0pP","f00mp0pS","rho1pp1pS","rho0mp0pP","rho2mp0pP","rho2mp1pP","f02mp0pD"]




bs_isob={
"rho1pp0pS":[['1-(1++)0+ rho pi S                                          '],'1-(1++)0+ rho1pp0pS pi S                                    ','rho'],
"rho2pp1pD":[['1-(2++)1+ rho pi D                                          '],'1-(2++)1+ rho2pp1pD pi D                                    ','rho'],
"f01pp0pP" :[['1-(1++)0+ (pipi)_S pi P                                     ','1-(1++)0+ f0(980) pi P                                      '],'1-(1++)0+ f01pp0pP pi P                                     ','f0'],
"f00mp0pS" :[['1-(0-+)0+ (pipi)_S pi S                                     ','1-(0-+)0+ f0(980) pi S                                      ' ,'1-(0-+)0+ f0(1500) pi S                                     '],
                                                                              '1-(0-+)0+ f00mp0pS pi S                                     ','f0'],
"rho1pp1pS":[['1-(1++)1+ rho pi S                                          '],'1-(1++)1+ rho1pp1pS pi S                                    ','rho'],
"rho0mp0pP":[['1-(0-+)0+ rho pi P                                          '],'1-(0-+)0+ rho0mp0pP pi P                                    ','rho'],
"rho2mp0pP":[['1-(2-+)0+ rho pi P                                          '],'1-(2-+)0+ rho2mp0pP pi P                                    ','rho'],
"rho2mp1pP":[['1-(2-+)1+ rho pi P                                          '],'1-(2-+)1+ rho2mp1pP pi P                                    ','rho'],
"f02mp0pD" :[['1-(2-+)0+ (pipi)_S pi D                                     ','1-(2-+)0+ f0(980) pi D                                      '],'1-(2-+)0+ f02mp0pD pi D                                     ','f0']
}

def string_to_length(string, n=60):
	if len(string)== n:
		return string
	if len(string) > n:
		return string[:n]
	while len(string) < 60:
		string+=' '
	return string
	
#template = 'template_bootstrap.dat'
#template = 'template_bootstrap_MC.dat'
def create_bootstrap(		name,
				modestring,
				template = 'template_bootstrap_MC.dat',
				bs_path = None,
				cardfolder = '/nfs/hicran/project/compass/analysis/fkrinner/fkrinner/trunk/MassIndependentFit/cards/'):

	in_file = open(cardfolder+'/'+template,'r')
	out_file= open(cardfolder+'/card_'+name+'.dat','w')

	mode={
		"rho1pp0pS":'u',
		"rho2pp1pD":'u',
		"f01pp0pP" :'u',
		"f00mp0pS" :'u',
		"rho1pp1pS":'u',
		"rho0mp0pP":'u',
		"rho2mp0pP":'u',
		"rho2mp1pP":'u',
		"f02mp0pD" :'u'
	}

	if not len(bootstrapped) == len(modestring):
		raise IndexError("Wrong length of the modestring")
	else:
		for i in range(len(bootstrapped)):
			if not modestring[i] in ['b','i','d','0']:
				raise ValueError("Unknown mode: '"+modestring[i]+"'")
			mode[bootstrapped[i]] = modestring[i]

	for bs in bootstrapped:
		out_file.write('C '+bs)
		if mode[bs] == 'b':
			out_file.write(':\tboostrapped isobar\n')	
		if mode[bs] == 'i':
			out_file.write(':\tnormal isobar\n')
		if mode[bs] == 'd':
			out_file.write(':\tde-isobarred\n')
		if mode[bs] == '0':
			out_file.write(':\tnot used\n')
	if bs_path:
		out_file.write("PATH_LOAD_BOOTSTRAP  '"+bs_path+"'\n")

	for line in in_file.readlines():
		if not '<' in line:
			out_file.write(line)
		else:
			chunks = line.split('<')
			if chunks[1] ==  'addwavefile':
				out_file.write(line.replace('<addwavefile<',"'addwave_"+name+".dat'"))
			elif chunks[1] in bootstrapped:
				key = chunks[1]
				out_file.write('C--------------------'+key+'--------------------------------------------------------------------\n')
				if mode[key] == 'b':
					out_file.write("*IWAVENAM '"+bs_isob[key][1]+"'\n")
				if mode[key] == 'i':
					for wave in bs_isob[key][0]:
						out_file.write("*IWAVENAM '"+wave+"'\n")
				if mode[key] == 'd':
					de_isobars=open(cardfolder+'/de_isobarred_'+bs_isob[key][2]+'.dat','r')				
					for de_isob in de_isobars:
						out_file.write("*IWAVENAM '"+string_to_length(bs_isob[key][1].replace(key,de_isob.strip().split()[0]))+"'    0     0     0   "+de_isob.strip().split()[1]+'\n')
					de_isobars.close()
				if mode[key] =='0':
					pass
				out_file.write('C--------------------'+key+'--------------------------------------------------------------------\n')
			else:
				raise ValueError('Unkown marker: '+chunks[1])
		
	out_file.close()
	in_file.close()

	card=open(cardfolder+"/card_"+name+".dat","r")
	addwave=open(cardfolder+"/addwave_"+name+".dat",'w')
	for line in card.readlines():
		if line.strip().startswith('*IWAVENAM'):
			chunks=line.strip().split("'")
			addwave.write("*ADDWAVE  '"+chunks[1]+"'\n")
		if line.strip().startswith('*IWAVENAM_NAMDEP'):
			addwave.write(line.replace("*IWAVENAM_NAMDEP","*ADDWAVE_NAMDEP"))

	addwave.write("*ADDWAVE  '1-(2++)2- f2 pi P                                           '\n*ADDWAVE  '1-(2++)1- rho pi D                                          '")#For some reason, the second to last integral is doubled and the last one omitted, so none of them may appear in the fit.
	addwave.close()
	card.close()


if __name__ == "__main__":
	if len(argv)>1:
		name = argv[1]

	if len(argv)>2:
		modestring = argv[2]


	template = None
	if len(argv)>3:
		template = argv[3]

	bs_path = None
	if len(argv)>4:
		bs_path = argv[4]
		if not bs_path.endswith("/"):
			bs_path+="/"

	if template:
		if bs_path:
			create_bootstrap(name,modestring,template,bs_path)
		else:
			create_bootstrap(name,modestring,template)
	else:
		create_bootstrap(name,modestring)






