#!/usr/bin/python 

########################## FHIRfetch.py #########################
# Author: SG Langer Sept 2018
#
# Purpose: take command line args to seach the FHIR index and 
#	return a list of URLS to image series matching search spec
#
################################################################
import os, dicom, sys, commands
import json
from download_data import FHIR


if __name__ == '__main__':
############################# main ################
# Purpose: parse command line args 
#
#	arg[1] = organ
#	arg[2] = condition
#	arg[3] = study type
#	arg[4] = dump directory for series fetched
##################################################
	mod = 'FHIRfetch.py: main'
	os.system('clear')
	ROOT = '/home/sgl02/code/py-code/mlcBuilder/'

	# use cmd line arg to locate spec qry
	if len(sys.argv ) != 4 :
		print "Incorrect Usage: see below.  No trailing /" 
		print ">./FHIRfetch.py organ condition destination_directory "
		exit(1)
	else :
		ORGAN = sys.argv[1]
		COND = sys.argv[2]
		DEST = sys.argv[3]


	# create a connection to the FHIR server
	cur = FHIR('hackFHIR')
	fp = open(DEST + '/results.txt' , 'w')


	# get the COnditions that match Organ and Cond
	buf = cur.getConditions(ORGAN, COND)
#	print buf
	print '*****************************'
	print buf['total']

	# now find the dxReports for the patients found above
	# that have positive findings for the COndition
	i = 0
	while  i< buf['total'] :
		PID = buf['entry'][i]['resource']['subject']['reference']
		PID = PID[PID.find('/') + 1:]
		res = cur.getReports(PID)
		j = 0
		fp.write(PID + '\n')
		while j< res['total'] :
			rid = res['entry'][j]['resource']['identifier'][0]['value']  
			# and tie imagingStudy to the report
			stdyUID = cur.getImagingStudy (rid)
			stdyUID = stdyUID['entry'][0]['resource']['uid'] 
			str1 = 'report ' + rid + ' ' + res['entry'][j]['resource']['conclusion'] + ' studyUID = ' + stdyUID + '\n'
			fp.write(str1)
			j = j+1

		i = i +1


	# then parse over them for the right modality type

	fp.close()
	sys.exit(0)
