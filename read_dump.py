#!/usr/bin/python 

########################## read_dump.py #########################
# Author: SG Langer 30 Jan 2018
#
# Purpose: provide a set of classes to open/read various annotation
#	dbase dumps from public image archives
#
#
###############################################################
import os, string, zipfile
from download_data import tcia


class mdAI :
###################################################
# Purpose: call an mdAI dbase dump, determine the file
#	heirachy and start getting series in DICOM_DIR format
#
# External dependants: an mdAI JSON file
#
##################################################

	def getCondition(self, fp,UID):
	#########################################################
	# Purpose: crawls annotation dump for patient level condition
	#
	# fp = file handle to annoatation dump
	# UID = UID in the dbase dumpe to seach
	###########################################
		mod = 'read_dump.py:mdAI: getCondition'

		return 'cancer'

	def getFindings(self, fp, UID):
	#########################################################
	# Purpose: crawls annotation dump for stdy level findings
	#
	#
	###########################################
		mod = 'read_dump.py:mdAI: getFinding'

		return 'really big lump'


	def init(self, direc):
	######################################
	# Purpose: if called by an external, set
	#	global Vars
	#	
	########################################
		mod = 'read_dump.py:mdAI:init'
		global ROOT

		ROOT = direc
		return 0

	def harvest(self, projectDir):
	######################################
	# Purpose: Now mdAI's dump (and likely most) is Study root
	#		based so there is a good chance the same patient is
	#		scattered among several study folders. We consolidate them 
	#		here
	################################################
		mod = 'read_dump.py:mdAI: harvest'

		# first check if Hackathon folder exists
		if not (os.path.isdir(ROOT + 'HACKATHON/')) : os.system('mkdir ' + ROOT + '/HACKATHON/')

		# then check/make project folder under it
		if not (os.path.isdir(ROOT + 'HACKATHON/' + projectDir)) : os.system('mkdir ' + ROOT + 'HACKATHON/' + projectDir)

		# then crawl project folders to collect patients under the above
		pDir = ROOT + projectDir
		destination = ROOT + 'HACKATHON/' + projectDir
		os.system('cd ' + pDir)

		for root, dirs, files in os.walk(pDir)  :
			for UID in dirs :
				for r, d, f in os.walk(pDir + '/' + UID)  :
					for i in d :
						if (projectDir in i ) :
							path = destination + '/' + i
							thisDir = pDir + '/' + UID + '/' + i
							# now check if this patient jacket in Hackathon - copy there if not	
							if not (os.path.isdir(path) ) : 
								os.system('cp -R ' + thisDir + ' ' + destination )
							else:
								print i + ' is already in ' + destination
								# so Patient & Condtion are already there, just need to copy any new Reports to it
								thisDir = pDir + '/' + UID + '/' + i + '/DiagnosticReport/*.json'
								os.system('cp -R ' + thisDir + ' ' + destination )

		return 0


	def readDump(self, projectDIR, projectDump):
	######################################
	# Purpose: read the JSON dump. For every studyUID
	# 	see if we have alaready made that folder.
	#	If yes - move on
	# 	If no - then make folder - call TCIA to get series
	##########################################
		mod = 'read_dump.py:mdAI:readDUmp'

		fp = open ( ROOT + projectDump, 'r')
		buf = fp.readlines()
		fp.close

		pDir = ROOT + projectDIR
		if ( os.path.isdir(pDir) ):
			print "directory exists"
		else:
			os.system('mkdir ' + pDir)

		os.system('cd ' + pDir)
		# now the fun  starts. For each StudyUID in dump, locate the children
		# seriesUID and build a list of All of them
		buf2 = buf[0]
		end = 0
		cnt = 0
		while ( end < len(buf2) ):
			start = buf2.find('StudyInstanceUID') + 19
			end  = start + 64
			UID = buf2[start:end]
			# now make that study level folder
			if not (os.path.isdir(pDir + '/' + UID)) :	os.system('mkdir ' + pDir + '/' + UID)
			
			# now move into UID directory to make lists
			os.system('cd ' + pDir + '/' + UID)
			if not (os.path.isdir(pDir + '/' + UID + '/allSeries') ) :
				source = tcia()
				allSeries = source.getSeriesUIDs(UID)
				fw = open ( pDir + '/' + UID + '/allSeries', 'w')
				fw.write(str(allSeries))
				fw.close()

			# next build the annotated_list by comparing All to the dump
			if not (os.path.isdir(pDir + '/' + UID + '/annotatedSeries') ) :
				array = []
				fw = open (pDir + '/' + UID + '/allSeries', 'r')
				buf3 = fw.readlines()
				fw.close()
				for i in buf3[0].split(',') : 
					if (i[3:67] in  buf[0] ) : array.append(i[3:67])

				fw = open ( pDir + '/' + UID + '/annotatedSeries', 'w')
				fw.write(str(array))			
				fw.close()

			buf2 = buf2[end:]
			cnt =cnt + 1
			if (cnt > 4) : break

		return 0

	def getZips (self, project, lists) :
	######################################
	# Purpose: read the indicated list of 
	# 	seriesUIDs and fetch zips for it
	##########################################
		mod = 'read_dump.py:mdAI:getZips'

		pDir = ROOT + project
		os.system('cd ' + pDir)

		for root, dirs, files in os.walk(pDir)  :
			for UID in dirs :
				if not ( '.' in UID ) : break
				print "study " + UID
				if ('all' in lists) :
					fp =  open(pDir + '/' + UID + '/allSeries', 'r')
					start = 3
					end = 67
				else:
					fp =  open(pDir + '/' + UID + '/annotatedSeries', 'r')
					start = 2
					end = 66

				res = fp.readlines()
				fp.close()

				# now we are going to get a single image for the FHIRmaker
				#  and optionally a Zip  of the whole series for mdAI
				if not (os.path.isdir(pDir + '/' + UID + '/DCM')) :	os.system('mkdir ' + pDir + '/' + UID + '/DCM')
				for i in res[0].split(',') :
					print '*** series ' + i[start:end]
					src = tcia()
					resp = src.getImage( i[start:end])
					with open(pDir + '/' + UID + '/DCM/' + i[start:end] + '.dcm', 'wb') as fp: fp.write(resp)
					fp.close()

					#resp = src.getSeries( i[start:67])
					#with open(pDir + '/' + UID + '/DCM/' + i[start:end] + '.zip', 'wb') as fp: fp.write(resp)
	
		return 0


if __name__ == '__main__':
############################# main ################
# Purpose: figure out whose dump we are using and 
#	use it to start crawling image arch
#
#	This stub for unit testing
################################################
	mod = 'read_dump.py: main'
	os.system('clear')

	# build lists of all series and annotaed series for the dump
	ctr = mdAI()
	res = ctr.init('/home/sgl02/code/py-code/mlcBuilder/')
	res = ctr.readDump('tcia' , 'project_20_all_2018-01-27-130167.json')

	# then drop an image in each seriesFolder so that we have somethien to build FHIR from
	res= ctr.getZips('tcia', 'ann')
	
	# always call this last
	res = ctr.harvest('tcia')

	exit (0)

