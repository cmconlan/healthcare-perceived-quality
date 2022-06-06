

# %%

def addConsultationFees(survey,conversionFee):
    
    survey_costs = survey[['structure_id', 'household_id', 'q420a', 'q425a']]
    survey_costs.loc[survey_costs['q425a'] >= 7500, 'q425a'] = None
    
    #strip out nan values
    survey_costs = survey_costs[survey_costs['q425a'].notna()]
    
    # De Dupe on 'structure_id', 'household_id','q420a' keep highest
    survey_costs = survey_costs.sort_values(by=['structure_id', 'household_id', 'q420a', 'q425a'],
                                            ascending=[False, False, False, False])
    survey_costs = survey_costs.drop_duplicates(subset=['structure_id', 'household_id', 'q420a'], keep='first')
    
    # Match back to survey data
    survey_slum = survey_slum.merge(survey_costs, left_on=['structure_id', 'household_id', 'q420a'],
                                    right_on=['structure_id', 'household_id', 'q420a'], how="left")
    
    consultation_cost_dict = {}
    
    for fac in set(list(survey_slum['Facility ID'])):
        facility_temp = survey_slum[survey_slum['Facility ID'] == fac]['q425a']
        facility_temp = facility_temp.dropna()
    
        if facility_temp.shape[0] > 0:
            consultation_cost_dict[fac] = facility_temp.mean()
        else:
            consultation_cost_dict[fac] = 0
    
    survey_slum['Consultation Cost'] = survey_slum['q425a'].fillna(survey_slum['Facility ID'].map(consultation_cost_dict))
    
    # Conversion
    survey_slum['Consultation Fee Dollar'] = survey_slum['Consultation Cost'] * conversionFee
    consulationFees = survey_slum[['Facility ID','Consultation Fee Dollar']].groupby(['Facility ID']).mean()
    
    return consulationFees
    
# %%

def addWaitingTime(survey):

    waitingTimes = survey[['structure_id', 'household_id', 'q420a', 'q423_hr', 'q423_min']]
    
    for i in waitingTimes[waitingTimes['q423_hr'] == 98].index:
        waitingTimes.loc[i, 'q423_hr'] = 0
    
    for i in waitingTimes[waitingTimes['q423_min'] == 98].index:
        waitingTimes.loc[i, 'q423_min'] = 0
    
    for i in waitingTimes[waitingTimes['q423_hr'] > 3].index:
        waitingTimes.loc[i, 'q423_min'] = waitingTimes.loc[i, 'q423_hr']
        waitingTimes.loc[i, 'q423_hr'] = 0
    
    waitingTimes['totalWaitingMins'] = waitingTimes['q423_min'] + (waitingTimes['q423_hr'] * 60)
    
    # De Dupe on 'structure_id', 'household_id','q420a' keep highest
    waitingTimes = waitingTimes.sort_values(by=['structure_id', 'household_id', 'q420a', 'totalWaitingMins'],
                                            ascending=[False, False, False, False])
    waitingTimes = waitingTimes.drop_duplicates(subset=['structure_id', 'household_id', 'q420a'], keep='first')
    
    # Match back to survey data
    survey_slum = survey_slum.merge(waitingTimes[['structure_id', 'household_id', 'q420a', 'totalWaitingMins']],
                                    left_on=['structure_id', 'household_id', 'q420a'],
                                    right_on=['structure_id', 'household_id', 'q420a'], how="left")
    
    waitingTimeDict = {}
    
    for fac in set(list(survey_slum['Facility ID'])):
        facility_temp = survey_slum[survey_slum['Facility ID'] == fac]['totalWaitingMins']
        facility_temp = facility_temp.dropna()
    
        if facility_temp.shape[0] > 0:
            waitingTimeDict[fac] = facility_temp.mean()
        else:
            waitingTimeDict[fac] = 0
    
    survey_slum['totalWaitingMins'] = survey_slum['totalWaitingMins'].fillna(
        survey_slum['Facility ID'].map(waitingTimeDict))
    
    allWaitingTimes = survey_slum[['Facility ID', 'totalWaitingMins']].groupby(['Facility ID']).mean()
    
    return allWaitingTimes
    
