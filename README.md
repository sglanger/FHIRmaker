# FHIRmaker
crawl public medical imaging archives, create Patient and DiagnosticReport resources which in turn are discoverable via a FHIR API

# The Challenge
Let's say you are a Machine Learning researcher in medical imaging. You have a Keras model you woudl like to try out on lots of high Res Lung CT images. Ideally the resulting data sets (training and test) would have a mix of normals and positive findings that mimic the real world statistics. If you do not work at Ginormous Hospital, how do you locate all the publically avaiable datasets that could help you - and how much time would it take?

Enter FHIRmaker

# Theory
Lot's of people have image sets: NIH, other govt. agencies, foundations, etc. The issue is not images per se, but curation, annotation and -machine- discoverability. Imagine having a web page you could go to and type in the patient condition you are interested in (in ICD10 codes). Then, for those patients, the studies that display relevent finding for that condition and acquired via modalities (i.e MR) and imaging paramters (i.e Pulse sequence) your ML Model can use. 
