# %% Import Modules
import pandas as pd
from Scripts.utils import haversine
from Scripts.geoAnalysis import getRoadAndPathwayNetwork
from Scripts.dataWrangling import addConsultationFees, addWaitingTime


# %% Set parameters

conversionFee = 1
dailyWage = 2
hoursWorked = 6
vot = (dailyWage/hoursWorked)
facility_quality = 1
# speed at meters per second
speed_walking = 2.5
tc_walk = 0
hc = 0
wt = 0


# %% Read in data

#CSV containing dwellings
dwellings = pd.read_csv('Data/dwellings.csv')
#CSV containing dwellings
facilities = pd.read_csv('Data/facilities.csv', index_col=0)
#CSV containing dwellings
dwelling_facility_distances = pd.read_csv('Data/DwellingToFacilityInfo.csv', index_col=[0, 1])

#Calculate distance to network
dwelling_facility_distances['Dist to Network'] = dwelling_facility_distances['Total Distance'] - \
                                                 dwelling_facility_distances['Path Length']

#Read in survey information
dtype_dict = {'structure_id': str, 'household_id': str}
survey_slum = pd.read_csv('Data/survey_with_facilities.csv', dtype=dtype_dict)

#Create data type with all structures
all_structures = pd.concat([facilities[['lon', 'lat']], dwellings[['lon', 'lat']]])

# Read in survey
survey = pd.read_csd('Data/SurveyResponses.csv')

#%% Get min and max lat/lon

gSite = getRoadAndPathwayNetwork(all_structures,'Data/boundary.shp')

#%% Get consultation fees

consulationFees = addConsultationFees(survey,conversionFee)

#Add consultation fee on dwelling to facility cost matrix
consulations_fees_append = []

for i, r in dwelling_facility_distances.iterrows():
    try:
        consulations_fees_append.append(consulationFees.loc[i[1]]['Consultation Fee Dollar'])
    except:
        consulations_fees_append.append(0)

dwelling_facility_distances['Consulatation Fee'] = consulations_fees_append

#%%

allWaitingTimes = addWaitingTime(survey)

# Add consultation fee on dwelling to facility cost matrix
waitingTimesAppend = []

for i, r in dwelling_facility_distances.iterrows():
    if i[1] in list(allWaitingTimes.index):
        waitingTimesAppend.append(allWaitingTimes.loc[i[1]]['totalWaitingMins'])
    else:
        waitingTimesAppend.append(0)

dwelling_facility_distances['Waiting Time'] = waitingTimesAppend

#%%

# Parameters
#vot = 1

#%% Calculate Access Cost

# VOT*(1.5WT + TT + ANT) + TC + HC
dwelling_facility_distances['Access Score'] = vot * ((1.5 * wt) + ((dwelling_facility_distances['Total Distance'] / 1000) / speed_walking) + (dwelling_facility_distances['Waiting Time'] / 60)) + tc_walk + hc
dwelling_facility_distances['Travel Time'] = (dwelling_facility_distances['Total Distance'] / 1000) / speed_walking

#%%

# Select Facility Users
dwelling_with_survey_responses = dwellings.merge(survey_slum[['structure_id', 'Facility ID']], left_on='struct_id', right_on='structure_id', how='left')
facility_users = dwelling_with_survey_responses[dwelling_with_survey_responses['Facility ID'].isin(list(facilities.index))]

# Get actual access score per facility
access_costs = []
euclid_dist = []
network_times = []

for index, row in facility_users.iterrows():
    access_costs.append(
        dwelling_facility_distances.loc[(row['structure_id'], row['Facility ID']), :]['Access Score'])
    network_times.append(
        dwelling_facility_distances.loc[(row['structure_id'], row['Facility ID']), :]['Travel Time'])
    euclid_dist.append(haversine(row['lon'], row['lat'], facilities.loc[row['Facility ID']]['lon'],
                                 facilities.loc[row['Facility ID']]['lat']))

facility_users['Actual Access Cost'] = access_costs
facility_users['Uclidean Distance'] = euclid_dist
facility_users['Network Times'] = network_times

# Get relative access matrix

user_access_scores = pd.DataFrame(index=list(facility_users['structure_id'].drop_duplicates()),
                                  columns=list(facilities.index))

for index, row in user_access_scores.iterrows():
    for i in range(0, row.shape[0]):
        user_access_scores.loc[index, row.index[i]] = dwelling_facility_distances.loc[
            (index, row.index[i]), 'Access Score']

user_travel_time = pd.DataFrame(index=list(facility_users['structure_id'].drop_duplicates()),
                                  columns=list(facilities.index))

for index, row in user_travel_time.iterrows():
    for i in range(0, row.shape[0]):
        user_travel_time.loc[index, row.index[i]] = dwelling_facility_distances.loc[(index, row.index[i]), 'Travel Time']

# Calculate Attractiveness
facilities['Visits'] = 0.0
facilities['Attractiveness Score'] = 0.0
facilities['Access Cost to Visit'] = 0.0
facilities['Bypass Cost'] = 0.0
facilities['Bypass Count'] = 0
facilities['Times Bypassed'] = 0

for index, row in facility_users.iterrows():
    # Get visited facilities details
    facility_attended_id = row['Facility ID']
    facility_type = facilities.loc[row['Facility ID']]['Category']
    facility_attended_cost = row['Actual Access Cost']

    #Get Travel time to facility to determine bypasses
    facility_attended_network_cost = row['Network Times']

    # Get access scores for current users to all facilities
    access_scores = user_access_scores.loc[row['structure_id']]
    # Sort lowest to highest
    access_scores = access_scores.sort_values()

    it_network_costs = user_travel_time.loc[row['structure_id']]
    it_network_costs = it_network_costs.sort_values()

    facilities.at[facility_attended_id, 'Visits'] += 1
    facilities.at[facility_attended_id, 'Access Cost to Visit'] += facility_attended_cost

    # Iterate through scores
    for i in range(0, access_scores.shape[0]):

        # Get details for next closest facility
        next_facility_id = access_scores.index[i]
        next_facility_type = facilities.loc[next_facility_id]['Category']
        next_facility_cost = access_scores.iloc[i]
        next_facility_dist = it_network_costs.iloc[i]

        # Calculate attractivness index
        attractiveness_index = (facility_attended_cost / next_facility_cost)

        # Check if facility bypassed
        # if facility_attended_id == next_facility_id:
        #     break

        if next_facility_dist > facility_attended_network_cost:
            break

        # Add Bypas Cost
        facilities.at[facility_attended_id, 'Bypass Cost'] += next_facility_cost
        facilities.at[facility_attended_id, 'Bypass Count'] += 1
        facilities.at[next_facility_id, 'Times Bypassed'] += 1

        # Updatre Attractiveness Score
        facilities.at[facility_attended_id, 'Attractiveness Score'] += attractiveness_index
        facilities.at[next_facility_id, 'Attractiveness Score'] -= attractiveness_index

facilities['Average Facilities Bypassed'] = 0.0
facilities['Bypass Cost Mean'] = 0.0
facilities['Access Cost Mean'] = 0.0
facilities['Consultation Cost Mean'] = 0.0

for i, r in facilities.iterrows():
    try:
        facilities.loc[i, 'Average Facilities Bypassed'] = round(r['Bypass Count'] / r['Visits'], 2)
    except:
        facilities.loc[i, 'Average Facilities Bypassed'] = 0

    try:
        facilities.loc[i, 'Bypass Cost Mean'] = round(r['Bypass Cost'] / r['Bypass Count'], 2)
    except:
        facilities.loc[i, 'Bypass Cost Mean'] = 0

    dwelling_costs = dwelling_facility_distances.loc[pd.IndexSlice[:, i], :]
    try:
        facilities.loc[i, 'Access Cost Mean'] = dwelling_costs['Access Score'].mean()
    except:
        facilities.loc[i, 'Access Cost Mean'] = 0

    try:
        facilities.loc[i, 'Consultation Cost Mean'] = dwelling_costs['Consulatation Fee'].mean()
    except:
        facilities.loc[i, 'Consultation Cost Mean'] = 0

# Output Results to Specific Folder
facilities.to_csv('Results/Facility Results.csv')