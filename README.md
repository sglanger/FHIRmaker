# FHIRmaker
Purpose: Crawl public, annotaed, medical imaging archives, based on those annotations create Patient, Condition, diagnosticReport and imagingStudy FHIR resources which in turn are discoverable via a FHIR API


# The Challenge
Let's say you are a Machine Learning researcher in medical imaging. You have a Keras model you would like to try out on many high resolution Lung CT images. Ideally the resulting datasets (training and inference) would have a mix of normals and positive findings that mimic the real world statistics. However, if one does not work at Ginormous Hospital, how can one locate all the publically available datasets that could provide statistical power - and how much time would it take?

Enter FHIRmaker

# Theory
Many people have image sets: NIH, other govt. agencies, foundations, etc. The issue is not images per se, but curation, annotation and -machine- discoverability. Imagine having a web page or API you could go to and type in the patient condition you are interested in (in ICD10  or SNOMED codes). Then, for those patients, find the studies that display relevent findings for that condition acquired via modalities (i.e MR) and imaging paramters (i.e Pulse sequence) your ML Model can use. Press "Submit" and within seconds get a return list of URL's where the target studies on public archives exist.

How?

There are several approaches one can take; some are easy and automated, others require significant human effort. But at the end of the day, the goal is to index every patient/study on public sites and <p>
a) create from that information a patient FHIR resource that matches the names used on the source site
<br>b) determine (via numerous methods) the "AI interesting" patient conditions and list them in the Patient resource then
<br>c) locate the studies for that patient, represent their findings in ACR-RADS (or similar) terms in the Diagnostic Report resource and acquisition parameters (e.g. coded in LOINC-RADLEX) in the imagingStudy resources and then
<br>d) aggregate the above resources on a single FHIR server with the above described Web page and API

# Status
<br>Week 1: created the first 3 files indicated below, validating FHIR object output, TCIA API
<br>Week 2: validated download_data.py "get" functions work as expected on Hackathon FHIR server
<br>Week 3: build out the DICOMweb API class to enable retrieving source images from DICOMweb VNA's
<br>Week 4: build the web page (pending, provides candidate patients lists for now matching body-part and condition)

# To Dos
<br>1) send FHIR objects to FHIR git repo (manually for now)
<br>1) complete the study level search on the web page

# Contents
<br>download_data.py ::	suite of classes to abstract RESTful calls to image archives
<br>read_dump.py ::			class to read JSON dump of a dbase after it annotates an Archive (should include findings)
<br>FHIRmaker.py ::			class to call the above 2, and based on info create Patient and Report FHIR objects

