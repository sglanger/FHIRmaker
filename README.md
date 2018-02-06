# FHIRmaker
crawl public medical imaging archives, create Patient and DiagnosticReport resources which in turn are discoverable via a FHIR API

# The Challenge
Let's say you are a Machine Learning researcher in medical imaging. You have a Keras model you woudl like to try out on lots of high Res Lung CT images. Ideally the resulting data sets (training and test) would have a mix of normals and positive findings that mimic the real world statistics. If you do not work at Ginormous Hospital, how do you locate all the publically avaiable datasets that could help you - and how much time would it take?

Enter FHIRmaker

# Theory
Lot's of people have image sets: NIH, other govt. agencies, foundations, etc. The issue is not images per se, but curation, annotation and -machine- discoverability. Imagine having a web page you could go to and type in the patient condition you are interested in (in ICD10 codes). Then, for those patients, the studies that display relevent findings for that condition and acquired via modalities (i.e MR) and imaging paramters (i.e Pulse sequence) your ML Model can use. Press "Submit" and within seconds get a return list of URL's where the target studies on public archives exist.

How?

There are several apparoaches one can take; some are easy and autoamted, others requires lot's of human effort. But at the end of the day, the goal is to index every patient/study on public sites and <p>
a) create from that information a patient FHIR resource that matches the names used on the site
<br>b) determine (via numerous methods) the patient conditions and list them in the Patient resource then
<br>c) locate the studies for that patient, represent their findings in RADLEX in the Diagnostic Report resource and then
<br>d) aggragate the above resources on a single FHIR server with the above described Web page

# Status
Week 1: created the first 3 files indicated below, validating FHIR object output

# To Dos
<br>1) send FHIR objects to FHIR git repo (manually for now)
<br>2) validate (with download_data.py) the "get" functions work as expected on FHIR server
<br>3) build the web page

# Contents
<br>download_data.py ::	suite of classes to abstract RESTful calls to image archives
<br>read_dump.py ::			class to read JSON dump of a dbase after it annotates an Archive (should include findings)
<br>FHIRmaker.py ::			class to call the above 2, and based on info create Patient and Report FHIR objects

