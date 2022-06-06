This repository has the software required to output results for a single slum as per the methodology laid out in the paper "Perceived quality of care and choice of healthcare provider in informal settlements"

To run this code the user will need to place the following data in the "Data" folder:

dwellings (csv)
facilities (csv)
DwellingToFacilityInfo (csv)
SurveyResponses (csv)
surveyWithFacilities (csv)

The specification of these data are as follows. Note the data used has been cleaned from survey data, and process which the use will need to carry out to their own spec.

File Spec: dwellings
Fields:
struct_id (string) (to uniquely identify each structure)
lat (float) (structure latitude coordinate)
lon (float) (structure longtitude coordinate)

File Spec: facilities
Fields:
hfc_id (string) (to uniquely identify each facility)
Facility name (string) (facility name)
Type (string) (clinic or hospital)
Funding (string) (private or public)
lat (float) (structure latitude coordinate)
lon (float) (structure longtitude coordinate)

File Spec: DwellingToFacilityInfo
Fields:
struct_id (string) (to uniquely identify each structure)
hfc_id (string) (to uniquely identify each facility)
Path Length (float) (lenght in of sortest path between the dwelling and facility)
Total Distance (float) (lenght in of sortest path plus access distance to the network between the dwelling and facility)

File Spec: SurveyResponses
Fields:
struct_id (string) (to uniquely identify each structure)
household_id (string) (to uniquely identify each household within structure)
User may add whichever question that are relevant. We use patient need, reported travel time, consultation cost and waiting time.

File Spec: surveyWithFacilities
Fields:
structure_id (string) (to uniquely identify each structure)
household_id (string) (to uniquely identify each household within structure)
Survey Facility Name (string) (reported facility name in idividual's survey)
Standardised Name (string) (a standardised name to account for spelling erros etc in reported facility names)
Facility ID (string) (to uniquely identify each facility)



To set up the environment the user will need to install Python 3.9, and then the following modules

osmnx (1.1.2)
networkx (2.7.1)
pandas (1.4.1)
geopandas (0.10.2)
numpy (1.22.3)