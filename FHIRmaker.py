#!/usr/bin/python 

########################## FHIRmaker.py #########################
# Author: SG Langer 30 Jan 2018
#
# Purpose: This is the top of the FHIRmaker process. Before running
#	this, read_dump has parsed the dump of a DICOM archive annotation
#	to capture sample images that were annoted.
#
#	Using those, this module crawls the project directory craated by
#	them, and uses the Image to scrape exam and patient demographics, 
#	and the annotation dump to get Dx and Findings (per study)
#
#	This module then creates the Patient,COndition and DiagnoticReport 
#	records that we will then push back to the Hackathon FHIR server
#
# External dependants: download_data.py, read_dump.py and the project
#	directory they create
###################################################################
import os, dicom, sys
import json
from pprint import pprint
from read_dump import mdAI
from datetime import datetime

global projectDir, ROOT, DUMP, PROJECT, ANNOTATE


def makeFHIR(UID) :
#############################################
# Purpose: Loop over all the studies/series we have
#	pulled from an archve, then despatch builders
#	for each FHIR resource
#
#########################################
	mod = 'FHIRmaker.py: makeFHIR'

	fhirRoot = projectDir + '/' + UID + '/' + PROJECT

	# first we will crack the series/image to get patient demographics
	if not (os.path.isdir(projectDir + '/' + UID + '/DCM') ) : 
		print "no DCM folder in study " + UID
		return 1
	else: 
		for root, dirs, files in os.walk(projectDir + '/' + UID + '/DCM/')  :
			for img in files :	
				if not ('.dcm' in img) : 
					break
				else:
					# we need an img for Pat and Exam demogs
					path = projectDir + '/' + UID + '/DCM/' + img
					fp = dicom.read_file(path)

					# now make FHIR root directory
					path = fhirRoot + '_' + fp.PatientName
					if not (os.path.isdir(path) ) : os.system('mkdir ' + path)

					# now start making objects, only need 1 each for Pat and Cond
					# but can have multiple reports objects
					makePatient(fp, path)
					makeCondition(fp, path, UID)
					makeDxReport(fp, path, UID)
					
	return 0


def makePatient (img, path) :
#############################################
# Purpose: use the DCM image to get demographics
#	to stuff the patient FHIR
#
#	Need to check and exit if object already done
#########################################
	mod = 'FHIRmaker.py: makePatient'
	skelDir = ROOT + 'skel/patient.json'

	# json read examples https://stackoverflow.com/questions/2835559/parsing-values-from-a-json-file
	# insert update examples https://stackoverflow.com/questions/13949637/how-to-update-json-file-with-python#13949837
	# pydicom http://pydicom.readthedocs.io/en/latest/pydicom_user_guide.html

	# check if this object is already done - exit if so
	if (os.path.isfile(path + '/Patient/patient.json') ) : return 0

	if not (os.path.isdir(path + '/Patient') ) : os.system('mkdir ' + path + '/Patient') 
	# now start stuffing patient.json - first open the stub
	fp = open(skelDir, 'r')
	jsn = json.load(fp)
	fp.close()

	# update buffer with demog from DCM image
	jsn['name'][0]['family'] = img.PatientName
	jsn['gender'] = img.PatientSex
	jsn['birthDate'] = img.PatientBirthDate
	jsn['id'] = img.PatientID


	# write updates back to FHIR object
	fq = open(path + '/Patient/patient.json', 'w')
	fq.write (json.dumps(jsn, indent=2) )
	fq.close()

	return 0 


def makeCondition (img, path, UID) :
#############################################
# Purpose: use the annotation dump (or other clues)
#	to stuff the FHIR condition
#
#
#########################################
	mod = 'FHIRmaker.py: makeCondition'
	skelDir = ROOT + 'skel/condition.json'

	# check if this object is already done - exit if so
	if (os.path.isfile(path + '/Condition/condition.json') ) : return 0

	if not (os.path.isdir(path + '/Condition') ) : 	os.system('mkdir ' + path + '/Condition') 
	# now start stuffing condition.json
	fp = open(skelDir, 'r')
	jsn = json.load(fp)
	fp.close()

	# update buffer with demog from DCM image
	jsn['patient']['reference'] = img.PatientID
	jsn['id'] = img.PatientID
	jsn['bodySite'][0]['text'] = img.BodyPartExamined

	# and get Condition(s) from the Annotation dbase dump - for now fake it
	ctr = mdAI()
	res = ctr.init(ROOT)
	jsn['code']['text'] = ctr.getCondition(ANNOTATE, UID)
	jsn['code']['coding'][0]['display'] = 	ctr.getFindings(ANNOTATE, UID)

	# write updates back to FHIR object
	fq = open(path + '/Condition/condition.json', 'w')
	fq.write (json.dumps(jsn, indent=2) )
	fq.close()

	return 0 


def makeDxReport (img, path, UID) :
#############################################
# Purpose: use the annotation dump to get the
#	findings per study and stuff each Dx report
#
#	UNlike the other 2 makes - this one can make
#	numerous instances of Report objects
#########################################
	mod = 'FHIRmaker.py: makePatient'
	skelDir = ROOT + 'skel/diagnosticReport.json'

	if not (os.path.isdir(path + '/DiagnosticReport') ) : os.system('mkdir ' + path + '/DiagnosticReport') 
	# now start stuffing patient.json
	fp = open(skelDir, 'r')
	jsn = json.load(fp)
	fp.close()

	# get finding(s) from the Annotation dbase dump
	ctr = mdAI()
	res = ctr.init(ROOT)
	ctr.getFindings(ANNOTATE, UID)
	jsn['id'] = img.StudyInstanceUID
	jsn['identifier'][0]['value'] = img.AccessionNumber
	jsn['code']['text'] = img.StudyDescription
	jsn['subject']['reference'] = img.PatientID
		
	# write updates back to FHIR object
	fq = open(path + '/DiagnosticReport/diagnosticReport_' + img.StudyInstanceUID + '.json', 'w')
	fq.write (json.dumps(jsn, indent=2) )
	fq.close()

	return 0 


if __name__ == '__main__':
############################# main ################
# Purpose: Validate the project directory is complete, 
#	then open the Annotation dump to get Dx and report findings.
#	Then image to get exam and Patient demographics. 
#
#	Then, use the combo to create and stuff the FHIR objects
#
########################################################
	mod = 'FHIRmaker.py: main'
	os.system('clear')
	ROOT = '/home/sgl02/code/py-code/mlcBuilder/'

	t_start = datetime.now()

	# use cmd line arg to locate projectDir
	if len(sys.argv ) != 3 :
		print "Incorrect Usage: Must include -project directory- and -dump file- No trailing /" 
		exit(1)
	else :
		projectDir = ROOT + sys.argv[1]  
		DUMP = sys.argv[2]
		PROJECT = sys.argv[1]

	# load Annoation dump file
	try :
		fp = open ( ROOT + DUMP, 'r')
		ANNOTATE = fp.readlines()
		fp.close
	except:
		print 'DUmp file does not exist'
		exit(1)

	# now try to get into it
	if (os.path.isdir(projectDir) ) :	
		os.system('cd ' + projectDir)
	else :
		print "project directory does not exist - use read_dump to create project " 
		#exit(1)
		# build lists of all series and annotaed series for the dump
		ctr = mdAI()
		res = ctr.init(ROOT)
		res = ctr.readDump(PROJECT , DUMP)
		# then drop an image in each seriesFolder so that we have somethien to build FHIR from
		res= ctr.getZips(PROJECT, 'ann')
		os.system('cd ' + projectDir)

	# it exists, let's light some FHIRs
	for root, dirs, files in os.walk(projectDir)  :
		for UID in dirs :
			if not ('.' in UID) : break
			res = makeFHIR(UID)

	# and last - we consolidate all the study FHIR objects under patient folders 
	# in HACKATHON + projectDir
	ctr = mdAI()
	res = ctr.init(ROOT)
	res = ctr.harvest(PROJECT)

	t_run = datetime.now() - t_start
	print "runtime " + str( t_run)
	exit(0)
