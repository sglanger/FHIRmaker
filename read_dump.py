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
from download_data import DCMweb

class bioPort :
###################################################
# Purpose: send text findings to REST API and get
#	back codes
#
# External dependants: 'sudo pip install requests"
#	http://data.bioontology.org/documentation
#
##################################################

	def __init__(self, baseURL, key):
	#######################################
	# Purpose: dump all patients on this
	# 	EMR. 
	#	
	##########################################
		self.url = baseURL
		self.api_key = key

		return


class mdAI :
###################################################
# Purpose: call an mdAI dbase dump, determine the file
#	heirachy and start getting series in DICOM_DIR format
#
# External dependants: an mdAI JSON file
#
##################################################


	def __init__(self, direc):
	######################################
	# Purpose: if called by an external, set
	#	global Vars
	#	
	########################################
		mod = 'read_dump.py:mdAI:init'
		self.ROOT = direc

		return 



	def harvest(self, projectDir):
	######################################
	# Purpose: Now mdAI's dump (and likely most) is Study root
	#		based so there is a good chance the same patient is
	#		scattered among several study folders. We consolidate them 
	#		here
	################################################
		mod = 'read_dump.py:mdAI: harvest'

		# first check if Hackathon folder exists
		if not (os.path.isdir(self.ROOT + 'HACKATHON/')) : os.system('mkdir ' + self.ROOT + '/HACKATHON/')

		# then check/make project folder under it
		if not (os.path.isdir(self.ROOT + 'HACKATHON/' + projectDir)) : os.system('mkdir ' + self.ROOT + 'HACKATHON/' + projectDir)

		# then crawl project folders to collect patients under the above
		pDir = self.ROOT + projectDir
		destination = self.ROOT + 'HACKATHON/' + projectDir
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
								#print i + ' is already in ' + destination
								# so Patient & Condtion are already there, just need to copy any new Reports and Imaging  to it
								thisDir = pDir + '/' + UID + '/' + i + '/DiagnosticReport/*.json'
								os.system('cp -R ' + thisDir + ' ' + destination )
								thisDir = pDir + '/' + UID + '/' + i + '/ImagingStudy/*.json'
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

		fp = open ( self.ROOT + projectDump, 'r')
		buf = fp.readlines()
		fp.close()		

		pDir = self.ROOT + projectDIR
		if ( os.path.isdir(pDir) ):
			print "directory exists"
		else:
			os.system('mkdir ' + pDir)

		os.system('cd ' + pDir)
		# now the fun  starts. For each StudyUID in dump, locate the child seriesUIDs and build a list of All of them
		buf2 = buf[0]
		# first get to where the annotations start, 
		buf2 = buf2[buf2.find('annotations":'):]

		end = 0
		cnt = 0
		while ( end < len(buf2) ):
			start = buf2.find('StudyInstanceUID') + 19
			end  = start + 120		
			UID = buf2[start:end]	
			UID = UID[0 : UID.find('"')]	# find true end of the UID (where the final " is)

			# now make that study level folder
			if not (os.path.isdir(pDir + '/' + UID)) :	os.system('mkdir ' + pDir + '/' + UID)
			
			# now move into studyUID directory to make lists
			os.system('cd ' + pDir + '/' + UID)

			# Now, check VNA for all series under this studyUID	
			if not (os.path.isdir(pDir + '/' + UID + '/allSeries') ) :
				# Magic happens here - in download_data we handle two Image archive APIs
				# either TCIA's  ....
				if projectDIR ==  "tcia" :
					source = tcia('tcia')
					allSeries = source.getSeriesUIDs(UID)
				else :
					# or DICOMweb API
					source = DCMweb('hackDCM')
					allSeries = source.getSeriesUIDs(UID)
					#print mod + ' ' + str(allSeries)
		
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
					#print "raw " + i
					if ('u' in i) : i = i[i.find('u') + 2 :]			
					if ('\'' in i) : i = i[:i.find('\'') ]
					#print " post " + i
					if (i in  buf[0] ) : 
						#print "found match in annotaed " + i
						array.append(i)

				fw = open ( pDir + '/' + UID + '/annotatedSeries', 'a')
				#print mod + ' annotaed array is ' + str(array)
				fw.write(str(array))			
				fw.close()

			buf2 = buf2[end:]
			cnt =cnt + 1
			if (cnt > 4) : break

		return 0


	def getImgs (self, project, lists):
	################################
	# Purpose: fetch a single image for each 
	#	annooated series so we have something to 
	#	build FHIR data from
	#
	# Caller: FHIRmaker:main DCMweb case
	#########################################
		mod = 'read_dump.py:mdAI:getImgs'

		pDir = self.ROOT + project
		os.system('cd ' + pDir)

		for root, dirs, files in os.walk(pDir)  :
			for UID in dirs :
				if not ( '.' in UID ) : break
				print mod + " study " + UID
				if ('all' in lists) :
					fp =  open(pDir + '/' + UID + '/allSeries', 'r')
				else:
					fp =  open(pDir + '/' + UID + '/annotatedSeries', 'r')

				res = fp.readlines()
				fp.close()

				# now we are going to get a single image from each indicated seriesUID
				if not (os.path.isdir(pDir + '/' + UID + '/DCM')) :	os.system('mkdir ' + pDir + '/' + UID + '/DCM')
				for i in res[0].split(',') :
					#print ' raw ' + i
					if ('[' in i ) : i =  i[i.find('[') + 2 :]
					if (']' in i ) : i =  i[:i.find(']') - 1 ]
					if ('\'' in i ) : i =  i[i.find('\'') + 1 :]
					print  ' *** series '  + i
					src = DCMweb('hackDCM')
					err, resp = src.getImage(UID, i)
					if not err :
						with open(pDir + '/' + UID + '/DCM/' + i + '.dcm', 'wb') as fp: fp.write(resp)
						fp.close()		
					else:
						print mod + ' unable to find an instance for ' , UID, i
						return 1

		return 0


	def getZips (self, project, lists) :
	######################################
	# Purpose: read the indicated list of 
	# 	seriesUIDs and fetch zips for that series
	#
	# Caller: FHIRmaker TCIA case
	##########################################
		mod = 'read_dump.py:mdAI:getZips'

		pDir = self.ROOT + project
		os.system('cd ' + pDir)

		for root, dirs, files in os.walk(pDir)  :
			for UID in dirs :
				if not ( '.' in UID ) : break
				print mod + ' study ' + UID
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
					src = tcia('tcia')
					resp = src.getImage( i[start:end])
					with open(pDir + '/' + UID + '/DCM/' + i[start:end] + '.dcm', 'wb') as fp: fp.write(resp)
					fp.close()

					#resp = src.getSeries( i[start:67])
					#with open(pDir + '/' + UID + '/DCM/' + i[start:end] + '.zip', 'wb') as fp: fp.write(resp)
	
		return 0


	def getConditionFindings(self, path,UID):
	#########################################################
	# Purpose: crawls annotation dump for patient level condition
	#
	# path = path to the the annoatation dump by the caller
	# UID = study level ID in the dbase dump to search for
	#
	# Called by: FHIRmaker:makeDxReport and  FHIRmaker:makeCOndition
	# NOtes: earlier versions of MD.ai did not provide this info
	######################################################
		mod = 'read_dump.py:mdAI: getConditionFindings'
		import json
		Condition = ' This MD.ai dump has no Condition codes for study ' + UID
		Findings = ' This MD.ai dump has no Finding codes for study ' + UID

		fp = open(path, 'r')
		jsn = json.load(fp)
		fp.close()

		try :
			i = 0
			cnt = 0
			while jsn:
				item =  jsn['datasets'][0]['annotations'][i]
				studyUID = item['StudyInstanceUID']
				if studyUID == UID :
					# can be multiple annotations for same study, concat results
					cnt = cnt + 1
					print mod + ' found annotation ' + cnt + ' for ' + UID
					if not ('None' in item['note']) :
						Condition = str(item['radlexTagIds'])
						Findings = str(item['note'])
						#Data =  str(item['data'])
						#print mod + ' ' + Findings + ' ' + Condition 
 					#break

				i = i+1
		except :
			a = 1

		return Condition, Findings


if __name__ == '__main__':
############################# main ################
# Purpose: figure out whose dump we are using and 
#	use it to start crawling image arch
#
#	This stub for unit testing
################################################
	mod = 'read_dump.py: main'
	os.system('clear')
	print "*****************"

	# Call class and set ROOT path
	ctr = mdAI('/home/sgl02/code/py-code/mlcBuilder/')

	############### TESTS for MD.ai dump on TCIA archive
	# build lists "all_series" and "annotaed_series" for the dump
	res = ctr.readDump('tcia' , 'project_20_all_2018-01-27-130167.json')
	# then drop an image in each seriesFolder so that we have somethien to build FHIR from
	#res= ctr.getZips('tcia', 'ann')
	# always call this last
	#res = ctr.harvest('tcia')

	############### Tests for  MD.ai dump on a DCMweb archive
	res = ctr.readDump('cxr','mdai_siim_project_x9N20BZa_annotations_labelgroup_all_2018-08-15-123730.json')
	ID = '1.2.276.0.7230010.3.1.2.8323329.1014.1517875165.916102'
	res = ctr.getConditionFindings( '/home/sgl02/code/py-code/mlcBuilder/mdai_siim_project_x9N20BZa_annotations_labelgroup_all_2018-08-15-123730.json', ID) 

	print res
	exit (0)

