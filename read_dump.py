#!/usr/bin/python 

########################## read_dump.py #########################
# Author: SG Langer 30 Jan 2018
#
# Purpose: provide a set of classes to open/read various annotation
#	dbase dumps from public image archives
#
#
###############################################################
import os, sys, commands, string, json
from download_data import tcia

global ROOT

class mdAI :
###################################################
# Purpose: call an mdAI dbase dump, determine the file
#	heirachy and start getting series in DICOM_DIR format
#
# External dependants: an mdAI JSON file
#
##################################################

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
				print allSeries
				fw = open ( pDir + '/' + UID + '/allSeries', 'w')
				fw.write(str(allSeries))

			# next build the annotated_list by comparing All to the dump



			# finally drop an image in each seriesFolder so that we have somethien to build FHIR from


			buf2 = buf2[end:]

		return 0

if __name__ == '__main__':
############################# main ################
# Purpose: figure out whose dump we are using and 
#	use it to start crawling image arch
#
#
################################################
	mod = 'read_dump.py'
	os.system('clear')

	ROOT = '/home/sgl02/code/py-code/mlcBuilder/'

	ctr = mdAI()
	res = ctr.readDump('tcia' , 'project_20_all_2018-01-27-130167.json')

	exit (0)

