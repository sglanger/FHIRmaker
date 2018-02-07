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
global projectDir, ROOT, DUMP, PROJECT


def makeFHIR(UID) :
#############################################
# Purpose: Loop over all the studies/series we have
#	pulled from an archve, then despatch builders
#	for each FHIR resource
#
#########################################
	mod = 'FHIRmaker.py: makeFHIR'
	patID = ''
	patGender = ''
	patDOB = ''
	ICD10 = ''
	demogPat = { 'patID':patID , 'patGender':patGender , 'patDOB':patDOB , 'condition':ICD10 } 

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
					# recall, we only need one img per series, after that can 'break'
					path = projectDir + '/' + UID + '/DCM/' + img
					fp = dicom.read_file(path)

					# now make FHIR root directory
					path = fhirRoot + '_' + fp.PatientName
					print fp.PatientName
					if not (os.path.isdir(path) ) : os.system('mkdir ' + path)

					makePatient(fp, path)
					makeCondition(fp, path)
					makeDxReport(fp, path)
					break

	return 0


def makePatient (fp, path) :
#############################################
# Purpose: use the DCM image to get demographics
#	to stuff the patient FHIR
#
#
#########################################
	mod = 'FHIRmaker.py: makePatient'
	skelDir = ROOT + 'skel/patient.json'

	if not (os.path.isdir(path + '/Patient') ) : 
		os.system('mkdir ' + path + '/Patient') 
		os.system('cp ' + skelDir + ' ' + path + '/Patient')

	# now start stuffing patient.json

	return 0 


def makeCondition (fp, path) :
#############################################
# Purpose: use the annotation dump (or other clues)
#	to stuff the FHIR condition
#
#
#########################################
	mod = 'FHIRmaker.py: makePatient'
	skelDir = ROOT + 'skel/condition.json'

	if not (os.path.isdir(path + '/Condition') ) : 
		os.system('mkdir ' + path + '/Condition') 
		os.system('cp ' + skelDir + ' ' + path + '/Condition')

	# now start stuffing patient.json

	return 0 


def makeDxReport (fp, path) :
#############################################
# Purpose: use the annotation dump to get the
#	findings per study and stuff each Dx report
#
#
#########################################
	mod = 'FHIRmaker.py: makePatient'
	skelDir = ROOT + 'skel/diagnosticReport.json'

	if not (os.path.isdir(path + '/DiagnosticReport') ) : 
		os.system('mkdir ' + path + '/DiagnosticReport') 
		os.system('cp ' + skelDir + ' ' + path + '/DiagnosticReport')

	# now start stuffing patient.json

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

	# use cmd line arg to locate projectDir
	if len(sys.argv ) != 3 :
		print "Incorrect Usage: Must include -project directory- and -dump file- No trailing /" 
		exit(0)
	else :
		projectDir = ROOT + sys.argv[1]  
		DUMP = sys.argv[2]
		PROJECT = sys.argv[1]

	# load dump file
	try :
		fp = open ( ROOT + DUMP, 'r')
		dump = fp.readlines()
		fp.close
	except:
		print 'DUmp file does not exist'
		exit(0)

	# now try to get into it
	if (os.path.isdir(projectDir) ) :	
		os.system('cd ' + projectDir)
	else :
		print "project directory does not exist " 
		exit(0)	

	# it exists, lets get to work
	for root, dirs, files in os.walk(projectDir)  :
		for UID in dirs :
			if not ('.' in UID) : break
			res = makeFHIR(UID)
			print res


	exit(0)
