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
import os, dicom, sys, commands
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
			img = files[0]
			if not ('.dcm' in img) : 
				break
			else:
				# we need an img for Pat and Exam demogs
				path = projectDir + '/' + UID + '/DCM/' + img
				fp = dicom.read_file(path)

				# now make FHIR root directory
				path = fhirRoot + '_' + fp.PatientName
				if not (os.path.isdir(path) ) : os.system('mkdir ' + path)

				makePatient(fp, path)
				makeCondition(fp, path, UID)
				makeDxReport(fp, path, UID)
				makeImagingStudy(fp, path, UID)
					
	return 0


def makePatient (img, path) :
#############################################
# Purpose: use the DCM image to get demographics
#	to stuff the patient FHIR
#
#	
#########################################
	mod = 'FHIRmaker.py: makePatient'
	skelDir = ROOT + 'skel/patient.json'

	# json read examples https://stackoverflow.com/questions/2835559/parsing-values-from-a-json-file
	# json insert/update examples https://stackoverflow.com/questions/13949637/how-to-update-json-file-with-python#13949837
	# pydicom http://pydicom.readthedocs.io/en/latest/pydicom_user_guide.html
	# snomed https://snomedbrowser.com/Codes/Details/228084000

	if not (os.path.isdir(path + '/Patient') ) : os.system('mkdir ' + path + '/Patient') 
	# now start stuffing patient.json - first open the stub
	fp = open(skelDir, 'r')
	jsn = json.load(fp)
	fp.close()

	# update buffer with demog from DCM image
	jsn['id'] = img.PatientID
	jsn['text']['div'] = "<div xmlns=\"http://www.w3.org/1999/xhtml\">19 February Patient Feature pending</div>"
	jsn['identifier'][0]['value'] = img.PatientID
	jsn['identifier'][0]['assigner']['display'] = PROJECT
	jsn['name'][0]['family'] = img.PatientName
	jsn['gender'] = img.PatientSex
	jsn['birthDate'] = img.PatientBirthDate

	# write updates back to FHIR object
	fq = open(path + '/Patient/patient.json', 'w')
	fq.write (json.dumps(jsn, sort_keys=True, indent=2) )
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

	if not (os.path.isdir(path + '/Condition') ) : 	os.system('mkdir ' + path + '/Condition') 
	# now start stuffing condition.json
	fp = open(skelDir, 'r')
	jsn = json.load(fp)
	fp.close()

	# update buffer with demog from DCM image
	jsn['id'] = img.PatientID
	jsn['text']['div'] = "<div xmlns=\"http://www.w3.org/1999/xhtml\">19 February Condition Feature pending</div>"
	jsn['patient']['reference'] =  img.PatientName
	jsn['bodySite'][0]['text'] = img.BodyPartExamined
	jsn['bodySite'][0]['coding'][0]['display'] = img.BodyPartExamined

	# and get Condition(s) from the Annotation dbase dump - for now fake it
	ctr = mdAI()
	res = ctr.init(ROOT)
	jsn['code']['text'] = ctr.getCondition(ANNOTATE, UID)
	jsn['code']['coding'][0]['display'] = 	ctr.getCondition(ANNOTATE, UID)

	# write updates back to FHIR object
	fq = open(path + '/Condition/condition.json', 'w')
	fq.write (json.dumps(jsn, sort_keys=True, indent=2) )
	fq.close()

	return 0 


def makeDxReport (img, path, UID) :
#############################################
# Purpose: use the annotation dump to get the
#	findings per study and stuff each Dx report
#
#########################################
	mod = 'FHIRmaker.py: makeDxReport'
	skelDir = ROOT + 'skel/diagnosticReport.json'

	if not (os.path.isdir(path + '/DiagnosticReport') ) : os.system('mkdir ' + path + '/DiagnosticReport') 
	# now start stuffing patient.json
	fp = open(skelDir, 'r')
	jsn = json.load(fp)
	fp.close()

	jsn['id'] =  img.PatientID
	jsn['code']['coding'][0]['code'] = img.AccessionNumber
	jsn['code']['text'] = img.StudyDescription
	jsn['issued'] = img.StudyDate

	jsn['identifier'][0]['value'] = img.PatientID
	jsn['subject']['reference'] = img.PatientName
	jsn['effectiveDateTime'] = img.StudyDate

	# get finding(s) from the Annotation dbase dump
	ctr = mdAI()
	res = ctr.init(ROOT)
	jsn['conclusion'] = ctr.getFindings(ANNOTATE, UID)
		
	# write updates back to FHIR object
	fq = open(path + '/DiagnosticReport/diagnosticReport_' + img.StudyInstanceUID + '.json', 'w')
	fq.write (json.dumps(jsn, sort_keys=True, indent=2) )
	fq.close()
	return 0 


def makeImagingStudy (img, path, UID) :
#############################################
# Purpose: create a json object that indexes all the 
#	series for the study UID
#
############################################
	mod = 'FHIRmaker.py: makeImagingStudy'
	skelDir = ROOT + 'skel/imagingStudy.json'
	rootDir = projectDir + '/' + UID + '/DCM'

	if not (os.path.isdir(path + '/ImagingStudy') ) : os.system('mkdir ' + path + '/ImagingStudy') 

	# now start stuffing imagingStudy.json
	# we start by reading in the stub file
	# we are not going to index every image, series Info is enough
	fp = open(skelDir, 'r')
	jsn = json.load(fp)
	fp.close()

	# study level stuff we can get from 'img'
	jsn['id'] = img.PatientID
	jsn['started'] = img.StudyDate
	jsn['uid'] = 'urn:oid:' + img.StudyInstanceUID
	jsn['patient']['reference']  = img.PatientName
	jsn['accession']['value'] = img.AccessionNumber
	jsn['description'] = img.StudyDescription
	status, output = commands.getstatusoutput('ls -l ' + rootDir + ' |grep -c dcm')
	jsn['numberOfSeries'] = int( output )

	# now how do I stuff an array of N series into a container of 1
	# https://stackoverflow.com/questions/35333187/how-can-i-insert-new-json-object-to-existing-json-file-in-the-middle-of-object
	files = [] 
	files = os.listdir( rootDir  )
	chunk = jsn['series'][0]
	cnt = 0

	# first use the stubfile and grow the series section to the size needed
	while cnt < ( len(files) -1)  : 
		jsn['series'].append(chunk)	
		cnt = cnt + 1

	# then we write out the file w/ all the Exam level info
	with open (path + '/ImagingStudy/imagingStudy_' + img.StudyInstanceUID + '.json', 'w') as fq : 
		json.dump(jsn, fq, sort_keys=True, indent=2)	

	# now we read  the in-progress file  -back in- so we can stuff the series data
	# by looping over the images in the DCM folder 
	fp = open(path + '/ImagingStudy/imagingStudy_' + img.StudyInstanceUID + '.json', 'r')
	jsn = json.load(fp)
	fp.close()

	# and now we can stuff the series array by looping over an img per each series
	cnt = 0
	while cnt < len(files)  :
		fp = dicom.read_file(rootDir + '/' + files[cnt])
		jsn['series'][cnt]['number'] = cnt + 1
		jsn['series'][cnt]['modality']['code'] = fp.Modality
		jsn['series'][cnt]['modality']['vendor'] = fp.Manufacturer
		jsn['series'][cnt]['modality']['model'] = fp.ManufacturersModelName
		jsn['series'][cnt]['modality']['version'] = fp.SoftwareVersions
		jsn['series'][cnt]['uid'] = 'urn:oid:' + fp.SeriesInstanceUID
		jsn['series'][cnt]['description'] = fp.SeriesDescription
		jsn['series'][cnt]['started'] = fp.StudyDate
		cnt = cnt + 1
		#print fp.__dict__.keys()	

	# and finally write the finished  updates back to Imaging json object
	# https://stackoverflow.com/questions/21453117/json-dumps-not-working
	with open (path + '/ImagingStudy/imagingStudy_' + img.StudyInstanceUID + '.json', 'w') as fq : 
		json.dump(jsn, fq, sort_keys=True, indent=2)

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
		print ">./FHIRmaker.py project_folder project_annotation_file "
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
		res= ctr.getZips(PROJECT, 'all')
		os.system('cd ' + projectDir)

	# it exists, let's light some FHIRs
	for root, dirs, files in os.walk(projectDir)  :
		for UID in dirs :
			if not ('.' in UID) : break
			res = makeFHIR(UID)

	# and last - we consolidate all the study FHIR objects under patient folders 
	# in HACKATHON + projectDir
	# assure multiple Reports and Imaging objects have unique names so Harvest does not over-write priors
	ctr = mdAI()
	res = ctr.init(ROOT)
	res = ctr.harvest(PROJECT)

	print "runtime = " + str( datetime.now() - t_start)
	exit(0)
