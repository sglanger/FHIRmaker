#!/usr/bin/python 

########################## download_data.py ####################
# Author: SG Langer 30 Jan 2018
#
# Purpose: Abstract  all Web connections to various Archives into a class. 
#	GIven a UID for a DICOM study, pull it down and write it to local disk
#
# External dependants: called by the mlcREADER
#
# Usage: in most cases (exceptions are listed in the Class headers)
#	> from download_data import Class
#	> source=class()
#	> study = source.getStudy(UID)
#
#	From this point the normal Python dbase API is used
#############################################################



class hackathonFHIR :
###################################################
# Purpose: handle calls to Hackathon FHIR server
#
# External dependants: 'sudo pip install requests"
#
##################################################
	api_key = 'get your own'
	url = 'http://api.hackathon.siim.org/fhir/'

	def getPatients(self):
	######################################
	# Purpose: dump all patients on this
	# 	EMR. 
	#	
	##########################################
		mod = 'download_data.py:hackathonFHIR:getPatients'
		addon = 'Patient/'

		url1 = self.url + addon
		#		cmd = 'curl --request GET  --url url --header Accept: "application/json" --header apikey: api_key ' 
		#print url1

		import requests
		headers = {
    		'Accept': "application/json",
    		'apikey': self.api_key
    		}

		response = requests.request("GET", url1, headers=headers)
		return  response.text

	def getPatient(self, UID):
	######################################
	# Purpose: dump Patient resource 
	# 	for a single patient
	#	
	##########################################
		mod = 'download_data.py:hackathonFHIR:getPatient'
		addon = 'Patient/' + UID
		url1 = self.url + addon

		import requests
		headers = {
    		'Accept': "application/json",
    		'apikey': self.api_key
    		}

		response = requests.request("GET", url1, headers=headers)
		return  response.text

	def getReports(self, PID):
	######################################
	# Purpose: dump Patient report ID's 
	# 	for a single patient
	#	
	##########################################
		mod = 'download_data.py:hackathonFHIR:getReports'
		addon = 'DiagnosticReport?patient=' + PID
		url1 = self.url + addon
		print url1

		import requests
		headers = {
    		'Accept': "application/json",
    		'apikey': self.api_key
    		}

		response = requests.request("GET", url1, headers=headers)
		return  response.text

	def getReport(self, PID, RID):
	######################################
	# Purpose: dump report  
	# 	for a single patient
	#	
	##########################################
		mod = 'download_data.py:hackathonFHIR:getReport'
		addon = 'Patient/' + PID + '/' + RID
		url1 = self.url + addon
		print url1

		import requests
		headers = {
    		'Accept': "application/json",
    		'apikey': self.api_key
    		}

		response = requests.request("GET", url1, headers=headers)
		return  response.text

		
class hackathonDCM :
###################################################
# Purpose: handle calls to Hackathon DCMweb server
#
# External dependants: 
#
##################################################
	api_key = 'get your own'
	url = 'http://api.hackathon.siim.org/dicomweb/'

	def getStudies(self):
	######################################
	# Purpose: get list of all studies in
	# 		VNA
	#	
	##########################################
		mod = 'download_data.py:hackathonDCM:getStudies'
		addon = 'studies/'

		url1 = self.url + addon
		import requests

		headers = {
    		'Accept': "application/json",
    		'apikey': self.api_key
    		}

		response = requests.request("GET", url1, headers=headers)
		return  response.text


	def getStudy(self, UID):
	######################################
	# Purpose: get speific study mathcing UID
	# 
	#	
	##########################################
		mod = 'download_data.py:hackathonDCM:getStudies'
		addon = 'studies/' + UID

		url1 = self.url + addon
		import requests

		headers = {
    		'Accept': "application/json",
    		'apikey': self.api_key
    		}

		response = requests.request("GET", url1, headers=headers)
		return  response.text


class tcia :
###################################################
# Purpose: handle calls to TCGA dataset 
#
# External Requirments: 
##################################################
	api_key = 'get your own'
	url = 'https://services.cancerimagingarchive.net/services/v3/TCIA/query' 

	# TCIA uses older server where all REST options must be URL encoded
	# cannot use "headers" like above

	def getSeries(self, UID):
	#######################################
	# Purpose: get the zip file of the series
	#		referenced by the series UID
	###################################
		mod = 'download_data.py:TCGA:getSeries'
		addon= '/getImage?SeriesInstanceUID=' + UID + '&format=zip&api_key=' + self.api_key

		url1 = self.url + addon
		print url1

		# https://wiki.cancerimagingarchive.net/display/Public/TCIA+Programmatic+Interface+%28REST+API%29+Usage+Guide
		# https://github.com/TCIA-Community/TCIA-API-SDK/tree/master/tcia-rest-client-python

		import requests
		response = requests.request("GET", url1, headers="")
		return  response.text

	def getSeriesUIDs(self, UID):
	#######################################
	# Purpose: get the seriesUIDs for all
	#		series under the studyUID
	###################################
		mod = 'download_data.py:TCGA:getSeries'
		addon= '/getSeries?StudyInstanceUID=' + UID + '&format=json&api_key=' + self.api_key
		#addon = '/getCollectionValues?format=json&api_key=5d6a3e3f-16ef-47f5-b48c-5cf8d02138bb'		# for testiing

		url1 = self.url + addon
		print url1
	
		import requests
		response = requests.request("GET", url1, headers="")
		return  response.text


if __name__ == '__main__':
############################# main ################
# Purpose: Use command line args, get list of candidate
#	exams from RSNA edge dbase
#
# ARgs: rsnaFETCH.py 
# Caller: crontab?
################################################
	mod = 'download_data.py: hackathonDCM'

	import os
	from download_data import tcia
	os.system('clear')

	#source = hackathonFHIR()
	#ret = source.getPatient('siimsally')
	#print ret	
	#print "-----------------------"
	#ret = source.getReports('siimsally')
	
	source = tcia()
	ret = source.getSeriesUIDs ('1.3.6.1.4.1.14519.5.2.1.3344.4008.108477552695034703985419023766')
	print ret	

	exit (0)


