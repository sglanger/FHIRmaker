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
#	> source=class('site')
#	> study = source.getStudy(UID)
#
#	see -main- for more detailed usage examples
#############################################################


class FHIR :
###################################################
# Purpose: handle calls to Hackathon FHIR server
#
# External dependants: "sudo pip install requests"
#
##################################################
	# Hackathon FHIR url = 'http://hackathon.siim.org/fhir/'


	def __init__(self, site):
	#######################################
	# Purpose: set EMR base URL to call 
	# 	
	#
	# Caller: 	
	##########################################

		# build a dict for site data, thus collecting all keys here
		# first element is RESTful endpoint, second is API key
		str1 = ['http://hackathon.siim.org/fhir/', 'dd6f7f1d-1586-438f-8d35-ff589a12f4df']
		str2 = ['http://site.example.com/', 'new api key']
		site_dict = {'hackFHIR': str1, 'site2': str2}

		self.url = site_dict[site][0]
		self.api_key = site_dict[site][1]

		self.headers = {
    		'Accept': "application/json",
    		'apikey': self.api_key
    		}

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
		response = requests.request("GET", url1, headers=self.headers)
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
		response = requests.request("GET", url1, headers=self.headers)
		return  response.text

	def getCondition(self, PID) :
	######################################
	# Purpose: dump Condition resource 
	# 	for a single patient
	#	
	##########################################
		mod = 'download_data.py:hackathonFHIR:getCondition'
		addon = 'Condition?patient=' + PID
		url1 = self.url + addon

		import requests
		response = requests.request("GET", url1, headers=self.headers)
		return  response.text


	def getReports(self, PID):
	######################################
	# Purpose: dump report ID's 
	# 	for a single patient
	#	
	##########################################
		mod = 'download_data.py:hackathonFHIR:getReports'
		addon = 'DiagnosticReport?patient=' + PID
		url1 = self.url + addon

		import requests
		response = requests.request("GET", url1, headers=self.headers)
		return  response.text

	def getReport(self, PID, RID):
	######################################
	# Purpose: dump a report  
	# 	for a single patient
	#	
	##########################################
		mod = 'download_data.py:hackathonFHIR:getReport'
		addon = 'Patient/' + PID + '/' + RID
		url1 = self.url + addon

		import requests
		response = requests.request("GET", url1, headers=self.headers)
		return  response.text

		
class DCMweb :
###################################################
# Purpose: handle calls to any  DICOMweb compliant server
#
# External dependants: This class uses json lib to parse json
#
# Refs: https://www.orthanc-server.com/static.php?page=documentation
#	https://www.orthanc-server.com/users/rest.html
#
#	better off with https://www.dicomstandard.org/dicomweb/
##################################################


	def __init__(self, site):
	#######################################
	# Purpose: set the source VNA URL and authenticate 
	# 	
	#  site = index into the Connect Dict	
	##########################################

		# build a dict for site data, thus collecting all keys here
		# first element is RESTful endpoint, second is API key
		str1 = ['http://hackathon.siim.org/dicomweb/', 'dd6f7f1d-1586-438f-8d35-ff589a12f4df']
		str2 = ['http://site.example.com/', 'new api key']
		site_dict = {'hackDCM': str1, 'site2': str2}

		self.url = site_dict[site][0]
		self.api_key = site_dict[site][1]
		self.headers = {
    		'Accept': "application/json",
    		'apikey': self.api_key
    		}

		return

	def getPatients(self):
	######################################
	# Purpose: get list of all patients in
	# 		VNA
	#	
	##########################################
		mod = 'download_data.py:DCMweb:getStudies'
		# according to this link the below should get a result
		# https://docs.google.com/spreadsheets/d/e/2PACX-1vSBEymDKGZgskFEFF6yzge5JovGHPK_FIbEnW5a6SWUbPkX06tkoObUHh6T1XQhgj-HqFd0AWSnVFOv/pubhtml?gid=1094535210&single=true

		addon = 'patients/'
		url1 = self.url + addon

		import requests
		response = requests.request("GET", url1, headers=self.headers)
		return  response.text

	def getPatient(self, ID):
	######################################
	# Purpose: return JSON list of all studies 
	# 		for patient ID in VNA
	#
	# Note: see example 	https://www.dicomstandard.org/dicomweb/query-qido-rs/
	##########################################
		mod = 'download_data.py:DCMweb:getSeries'
		addon = '/studies/?00100020=' + ID + '?fuzzymatching=true'
		url1 = self.url + addon

		import requests
		response = requests.request("GET", url1, headers=self.headers)
		return  response.text


	def getImage(self, UID, ID):
	#######################################
	# Purpose: get a single image from the series
	#		referenced by the 
	# UID  = study UID and
	# ID  = series UID
	#
	# Caller: read_dump.py:mdAI:getImgs
	# Ref: https://github.com/clindatsci/dicomweb-client
	#		from apii.py: _http_get_application_dicom
	###################################
		mod = 'download_data.py:DCMweb:getImage'
		addon = 'studies/' + UID + '/series/' + ID + '/instances'
		url1 = self.url + addon
		err = 0
		hdr = {
    		'Content-Type':'multipart/related; type=image/dicom',
    		'apikey': self.api_key 
    		}
		
		import requests, json 
		# first get instance UIDs for this series
		response = requests.request("GET", url1, headers=self.headers)
		buf = json.loads(response.text)

		try :
			instanceURL = buf[0]['00081190']['Value'][0]
			instanceID = buf[0]['00080018']['Value'][0]
			# now we have the ID for a single image - get it
			addon=  'studies/' + UID + '/series/' + ID + '/instances/' + instanceID
			#print mod, ' addon is ' , addon
			url1 = self.url + addon

			r = requests.request("GET", url1, headers=hdr)
			resp = r.content											#111
			token = resp[resp.find('--'):7]
			resp = resp[resp.find('E-Version:') + 18: ]
			resp = resp[: resp.find(token)]
		except :
			print mod + ' study ' + UID 
			print ' not found on ' + self.url
			err = 1
			resp = 1

		return err, resp


	def getSeriesUIDs(self, UID):
	######################################
	# Purpose: get series UIDs for all series
	# 	under the incoming study UID
	#	
	##########################################
		mod = 'download_data.py:DCMweb:getSeriesUIDs'
		addon = 'studies/' + UID + '/series'
		array = []
		url1 = self.url + addon

		#print mod + " incoming id " + UID
		import requests, json
		response = requests.request("GET", url1, headers=self.headers)
		buf =  json.loads(response.text)

		try :
			i = 0
			while  (buf) :
					UID = buf[i]['0020000E']['Value'][0]
					#print mod + ' ' + UID
					array.append(UID)
					i = i +1
		except :
			a = 2

		return array


	def getSeriesURL(self, UID, ID):
	######################################
	# Purpose: take in study and series IDs and return
	#	the URL where it can be fetched
	#
	#####################################
		mod = 'download_data.py:DCMweb:getSeriesURL'
		# from https://www.dicomstandard.org/dicomweb/query-qido-rs/
		addon = 'studies/' + UID + '/series/' + ID + '/instances'
		url1 = self.url + addon

		import requests, json
		response = requests.request("GET", url1, headers=self.headers)
		buf =  response.text

		buf2 = buf[buf.find('http'):buf.find('instance')] 
		return buf2

	def getStudies(self):
	######################################
	# Purpose: dunmp a list of all studies
	#	on the VNA
	#
	#####################################
		mod = 'download_data.py:DCMweb:getStudies'
		addon = 'studies/' 
		url1 = self.url + addon

		import requests, json
		response = requests.request("GET", url1, headers=self.headers)
		buf =  json.loads(response.text)
		return buf


class tcia :
###################################################
# Purpose: handle calls to TCIA dataset 
#
# External Requirments: this class uses python string 
#	lib to parse json
##################################################


	def __init__(self, site):
	#######################################
	# Purpose: set the key and root URL for
	#	talking to TCIA
	#
	#####################################
		#addon = '/getCollectionValues?format=json&api_key=self.api_key'		# for testiing

		# build a dict for site data, thus collecting all keys here
		# first element is RESTful endpoint, second is API key
		str1 = ['https://services.cancerimagingarchive.net/services/v3/TCIA/query' , '5d6a3e3f-16ef-47f5-b48c-5cf8d02138bb']
		str2 = ['http://site.example.com/', 'new api key']
		site_dict = {'tcia': str1, 'site2': str2}

		self.url = site_dict[site][0]
		self.api_key = site_dict[site][1]

		# TCIA uses older server where all REST options must be URL encoded
		# cannot use "headers" like above classes
		return



	def getSeries(self, UID):
	#######################################
	# Purpose: get the zip file of the series
	#		referenced by the series UID
	###################################
		mod = 'download_data.py:TCIA:getSeries'
		addon= '/getImage?SeriesInstanceUID=' + UID + '&format=zip&api_key=' + self.api_key
		url1 = self.url + addon

		# print url1
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
	#
	# Caller: read_dump: getZips
	###################################
		mod = 'download_data.py:TCIA:getImage'
		addon= '/getSOPInstanceUIDs?SeriesInstanceUID=' + UID + '&format=json&api_key=' + self.api_key
		# example https://github.com/hilfikerp/TCIA-Python3-Downloader/blob/Menu-3.1/tciaclient.py

		# 2 steps, first get the instance UIDs in the series 
		url1 = self.url + addon

		import requests
		response = requests.request("GET", url1, headers="")
		buf = response.text
		#print mod + ' ' + buf
		start = buf.find('sop_instance_uid') + 19
		instanceUID = buf[start:86]

		# then fetch the image using both the series and instance UIDs
		addon='/getSingleImage?SeriesInstanceUID=' + UID + '&SOPInstanceUID=' + instanceUID  + '&api_key=' + self.api_key
		url1 = self.url + addon
		r = requests.get(url1, stream=True)
		resp = r.content
		return resp


	def getSeriesUIDs(self, UID):
	#######################################
	# Purpose: get the seriesUIDs for all
	#		series under the studyUID
	###################################
		mod = 'download_data.py:TCIA:getSeries'
		addon= '/getSeries?StudyInstanceUID=' + UID + '&format=json&api_key=' + self.api_key
		array = []
		url1 = self.url + addon

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
	print "-----------------------"

	# FHIR tests
	source = FHIR('hackFHIR')
	#ret = source.getPatient('siimjoe')
	#ret = source.getCondition('siimjoe')


	# DICOMweb tests
	source = DCMweb('hackDCM')
	study = '1.2.276.0.7230010.3.1.2.8323329.7070.1517875202.604896'					
	series = '1.2.276.0.7230010.3.1.3.8323329.7070.1517875202.604895'
	study2 = '1.2.276.0.7230010.3.1.2.8323329.11171.1517875231.515224'
	series2 = '1.2.276.0.7230010.3.1.3.8323329.11171.1517875231.515223'
	#ret = source.getSeriesUIDs(study2)
	#ret = source.getSeriesURL('1.3.6.1.4.1.14519.5.2.1.7777.9002.695251996732711525695705170858', '1.3.6.1.4.1.14519.5.2.1.7777.9002.605176515924083114740918850709')	
	#ret = source.getStudies()
	err, ret = source.getImage(study2, series2)
	if err :
		print 'fatal error - exiting'
	else :
		with open('/home/sgl02/code/py-code/mlcBuilder/img2.dcm', 'wb') as fp: fp.write(ret)
		fp.close()

	# TCIA API tests
	#source = tcia('tcia')
	#ret = source.getSeriesUIDs ('1.3.6.1.4.1.14519.5.2.1.3344.4008.824746819228131664143570751388')
	#resp= source.getImage ('1.3.6.1.4.1.14519.5.2.1.3344.4008.765690937215201567055591839620') 
	#resp = source.getSeries ('1.3.6.1.4.1.14519.5.2.1.3344.4008.765690937215201567055591839620') 
	#with open('img.dcm', 'wb') as fp: fp.write(resp)
	#fp.close()

	print ret
	exit (0)


