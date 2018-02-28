#!/usr/bin/python 

########################## download_data.py ####################
# Author: SG Langer 30 Jan 2018
#
# Purpose: Abstract  all Web connections to various Archives into a class. 
#	GIven a UID for a DICOM study, pull it down and write it to local disk
#
# External dependants: called by the FHIRaker
#						lib zipfile
#						lib dicom (sudo pip install dicom)
#
# Usage: in most cases (exceptions are listed in the Class headers)
#	> from download_data import Class
#	> source=class()
#	> study = source.getStudy(UID)
#
#	see _main_ for more
#############################################################


class FHIR :
###################################################
# Purpose: handle calls to Hackathon FHIR server
#
# External dependants: 'sudo pip install requests"
#
##################################################
	# Hackathon FHIR url = 'http://api.hackathon.siim.org/fhir/'


	def __init__(self, baseURL, key):
	#######################################
	# Purpose: dump all patients on this
	# 	EMR. 
	#	
	##########################################
		self.url = baseURL
		self.api_key = key

		return

	def getPatients(self):
	######################################
	# Purpose: dump all patients on this
	# 	EMR. 
	#	
	##########################################
		mod = 'download_data.py:hackathonFHIR:getPatients'
		addon = 'Patient/'
		url1 = self.url + addon

		#	cmd = 'curl --request GET  --url url --header Accept: "application/json" --header apikey: api_key ' 
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

	def getCondition(self, PID) :
	######################################
	# Purpose: dump Patient resource 
	# 	for a single patient
	#	
	##########################################
		mod = 'download_data.py:hackathonFHIR:getCondition'
		addon = 'Condition?patient=' + PID
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

		
class DCMweb :
###################################################
# Purpose: handle calls to Hackathon DCMweb server
#
# External dependants: 
#
##################################################

	# Hackathon DCMweb url = 'http://api.hackathon.siim.org/dicomweb/'


	def __init__(self, baseURL, key):
	#######################################
	# Purpose: dump all patients on this
	# 	EMR. 
	#	
	##########################################
		self.url = baseURL
		self.api_key = key

		return

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
	api_key = 'your key here'
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
		r = requests.get(url1, stream=True)
		resp = r.content
		return  resp


	def getImage(self, UID):
	#######################################
	# Purpose: get a single image from the series
	#		referenced by the series UID
	###################################
		mod = 'download_data.py:TCGA:getImage'
		addon= '/getSOPInstanceUIDs?SeriesInstanceUID=' + UID + '&format=json&api_key=' + self.api_key
		# example https://github.com/hilfikerp/TCIA-Python3-Downloader/blob/Menu-3.1/tciaclient.py

		# 2 steps, first get the instance UIDs in the series 
		url1 = self.url + addon
		#print url1

		import requests
		response = requests.request("GET", url1, headers="")
		buf = response.text
		start = buf.find('sop_instance_uid') + 19
		instanceUID = buf[start:86]

		# then fetch the image using both the series and instance UIDs
		addon='/getSingleImage?SeriesInstanceUID=' + UID + '&SOPInstanceUID=' + instanceUID  + '&api_key=' + self.api_key
		url1 = self.url + addon
		#print url1
		r = requests.get(url1, stream=True)
		resp = r.content
		return resp


	def getSeriesUIDs(self, UID):
	#######################################
	# Purpose: get the seriesUIDs for all
	#		series under the studyUID
	###################################
		mod = 'download_data.py:TCGA:getSeries'
		addon= '/getSeries?StudyInstanceUID=' + UID + '&format=json&api_key=' + self.api_key
		array = []
		url1 = self.url + addon
		print url1

		import requests
		resp = requests.request("GET", url1, headers="")
		buf = resp.text

		if (len(buf) < 10 ) : 
			return array
		else: 
			end = 0
			while  (end < len(buf)) :
				start = buf.find('{') + 22
				end = start + 64
				UID = buf[start:end]
				# print UID
				array.append(UID)
				buf = buf[end:]

		return  array



if __name__ == '__main__':
############################# main ################
# Purpose: Use command line args, get list of candidate
#	exams from RSNA edge dbase
#
#  also this stub for unit testing
################################################
	mod = 'download_data.py: main'

	import os, zipfile
	from download_data import tcia
	os.system('clear')

	source = FHIR('http://api.hackathon.siim.org/fhir/', 'your key here')
	ret = source.getPatient('siimsally')
	print ret	
	print "-----------------------"
	ret = source.getCondition('siimsally')
	print ret

	#source = tcia()
	#ret = source.getSeriesUIDs ('1.3.6.1.4.1.14519.5.2.1.3344.4008.824746819228131664143570751388')
	#resp= source.getImage ('1.3.6.1.4.1.14519.5.2.1.3344.4008.765690937215201567055591839620') 
	#resp = source.getSeries ('1.3.6.1.4.1.14519.5.2.1.3344.4008.765690937215201567055591839620') 
	#with open('img.dcm', 'wb') as fp: fp.write(resp)
	#fp.close()

	exit (0)


