# -*- coding: utf-8 -*-
"""
Created on Mon Nov  9 21:17:06 2015

@author: asjedh
"""
import pandas as pd
import numpy as py

os.chdir("/Users/asjedh/Desktop/DataForDiploma/data") #you may need to change this path
districts_merged = pd.read_csv("merged/graduation_with_census.csv")
districts_merged.shape

desired_cols = districts_merged.columns[0:27]
districts_merged = districts_merged[desired_cols]
districts_merged.rename(columns = {"ALL_RATE_1112": "clean_grad_rate"}, inplace = True)

districts_unmerged = pd.read_csv("unmerged/Graduation_Rates.csv")
districts_unmerged.columns
unmerged_only_grad_rate_and_leaid = districts_unmerged[["ALL_RATE_1112", "leaid11", "ALL_COHORT_1112"]]
merged_only_grad_rate_and_leaid = districts_merged[["clean_grad_rate", "leaid11"]]

compare_grad_rates = merged_only_grad_rate_and_leaid.merge(unmerged_only_grad_rate_and_leaid, on = "leaid11", how = "outer")

compare_grad_rates.to_csv("grad_rates_comparison.csv")

districts_merged_with_county_and_state_codes = districts_merged[["County", "State", "leaid11"]]

districts_unmerged = districts_unmerged.merge(districts_merged_with_county_and_state_codes, left_on = "leaid11", right_on = "leaid11")
# Clean up grad rate (dependent variables)
districts_unmerged.ALL_RATE_1112

#first get rid of all observations with no grad rate given. They all have PS as the ALL_RATE_1112
sum(districts_unmerged.ALL_RATE_1112 == "PS") #197

no_grad_rate = districts_unmerged.index[districts_unmerged.ALL_RATE_1112 == "PS"]

districts_unmerged.drop(no_grad_rate, inplace = True)

'''
Next, we need to make grad rates numeric. There are a few different types of values 
in the ALL_RATE_1112 column (the grad rate column). First, is just a number, which
is what we want. The others are ranges. The government provided ranges instead of
actual numbers because of privacy concerns. 

What we do is we get the median of any grad rate that is provided as a range. 
There are three different types of ranges. First, you have something like 60-64,
which is simple to parse.

The other two ranges look something like GE50 or LE50. They mean that the 
range is greater than/less than that number. Depending on whether it is greater
than or less than, I assigned the different floor/ceiling as 100 or 0, and then 
calculated the median of that range.

'''
districts_unmerged.ALL_RATE_1112


def get_median_grad_rate_in_range(grad_rate):
    no_hyphen = grad_rate.replace("-", "")
    half_length = len(no_hyphen) / 2

    first_number = int(no_hyphen[0:half_length])
    second_number = int(no_hyphen[half_length:])
    median = np.median([first_number, second_number])
    
    return median


def get_number_string_from_grad_rate_range(grad_rate):
    split_rate = list(grad_rate)
    digits = []
    
    for c in split_rate:
        try:
            int(c)
            digits.append(c)
        except:
            next
        
    grad_rate_string = "".join(digits)
    
    return grad_rate_string


def get_grad_rate_range(grad_rate):
    if "GE" in grad_rate:
        grad_rate_floor = get_number_string_from_grad_rate_range(grad_rate)
        grad_rate_ceiling = "100"
        
        grad_rate_range = grad_rate_floor + "-" + grad_rate_ceiling
    else:
        grad_rate_ceiling = get_number_string_from_grad_rate_range(grad_rate)
        grad_rate_floor = "0"
        
        grad_rate_range = grad_rate_floor + "-" + grad_rate_ceiling
    
    return grad_rate_range


def fix_grad_rate(grad_rate):
    try:
        clean_grad_rate = int(grad_rate)
        return clean_grad_rate
    except:
        if pd.isnull(grad_rate):
            next
        elif grad_rate == "PS":
            next
        elif "-" in grad_rate:
            clean_grad_rate = get_median_grad_rate_in_range(grad_rate)
            return clean_grad_rate
        else:
            grad_rate_range = get_grad_rate_range(grad_rate)
            clean_grad_rate = get_median_grad_rate_in_range(grad_rate_range)
            return clean_grad_rate
    
    
districts_unmerged.ALL_RATE_1112.apply(fix_grad_rate).astype(float)
districts_unmerged["clean_grad_rate"] = districts_unmerged.ALL_RATE_1112.apply(fix_grad_rate).astype(float)
districts_unmerged[["clean_grad_rate", "ALL_RATE_1112"]]
districts_unmerged.clean_grad_rate.describe()

districts_unmerged["native_american_grad_rates"] = districts_unmerged.MAM_RATE_1112.apply(fix_grad_rate).astype(float)
districts_unmerged["asian_pacific_islander_grad_rates"] = districts_unmerged.MAS_RATE_1112.apply(fix_grad_rate).astype(float)
districts_unmerged["black_grad_rates"] = districts_unmerged.MBL_RATE_1112.apply(fix_grad_rate).astype(float)
districts_unmerged["hispanic_grad_rates"] = districts_unmerged.MHI_RATE_1112.apply(fix_grad_rate).astype(float)
districts_unmerged["two_or_more_races_grad_rates"] = districts_unmerged.MTR_RATE_1112.apply(fix_grad_rate).astype(float)
districts_unmerged["white_grad_rates"] = districts_unmerged.MWH_RATE_1112.apply(fix_grad_rate).astype(float)
districts_unmerged["disability_grad_rates"] = districts_unmerged.CWD_RATE_1112.apply(fix_grad_rate).astype(float)
districts_unmerged["economically_disadvantaged_grad_rates"] = districts_unmerged.ECD_RATE_1112.apply(fix_grad_rate).astype(float)
districts_unmerged["limited_english_proficiency_grad_rates"] = districts_unmerged.LEP_RATE_1112.apply(fix_grad_rate).astype(float)


##### 2) READ IN OTHER DATASETS, MERGE TRACT DATA WITH DISTRICT CODES, CREATE WEIGHTED VALUES
# A. read in other datasets and merge tract data with district codes
tracts = pd.read_csv("unmerged/Census_Data_2010.csv")
overlap = pd.read_csv("unmerged/SD_TRACT_MAPPING2010.csv") #this dataset maps tracts with districts, and includes the percentage overlap

tracts.columns[0:20]
tracts.Tot_Population_CEN_2010.sum()
# Time to merge tracts and overlap!

overlap.columns
tracts.columns

overlap.State
overlap.County
overlap["Tract Code"]

overlap_merge_columns = ["State", "County", "Tract Code"]

tracts.State
tracts.County
tracts.Tract

tract_merge_columns = ["State", "County", "Tract"]

overlap_tracts_merge = overlap.merge(tracts, left_on = overlap_merge_columns, right_on = tract_merge_columns, how = "inner")

overlap_tracts_merge.shape
overlap_tracts_merge.Percentage.describe()

tracts.shape
overlap_tracts_merge.shape

'''
Here, I drop the margin of error (MOE) and calculated percentage columns.
The MOEs are not needed, and the calculated percentage cols will need to 
be recalculated after weighting and aggregating.
'''

for col in overlap_tracts_merge.columns:
    if "MOE" in col or "avg" in col or "pct" in col:
        overlap_tracts_merge.drop(col, axis = 1, inplace = True)

overlap_tracts_merge.shape

# C. Get weighted values using the tract-district overlap percentages

#This function is needed to convert some of the columns which are strings to floats
def turn_dollars_into_float(x):
    if pd.notnull(x):
        return float(x.replace("$", "").replace(",",""))
    else:
        return x
        
def fix_data_if_object_dtype(col):
    if overlap_tracts_merge[col].dtype == "object":
        overlap_tracts_merge[col] = overlap_tracts_merge[col].apply(lambda x: turn_dollars_into_float(x))

def create_new_weighted_column(col):
    weighted_col_name = "weighted_" + col
    weighted_col_value = (overlap_tracts_merge.Percentage / 100) * overlap_tracts_merge[col]
    overlap_tracts_merge[weighted_col_name] = weighted_col_value

# For all the columns that we need, I create weighted values for them based on the overlap percentages
for col in overlap_tracts_merge.columns[15:]:
    #this will turn all dollar values in string format into floats
    fix_data_if_object_dtype(col) 
    #ignore median income/value columns because they can't be calculated like this
    if "Med" not in col:
        create_new_weighted_column(col)

#make sure merge look generally accurate
overlap_tracts_merge.columns
overlap_tracts_merge.shape
overlap_tracts_merge.Percentage.describe()
tracts.Tot_Population_CEN_2010.sum()
overlap_tracts_merge.Tot_Population_CEN_2010.sum()
overlap_tracts_merge.weighted_Tot_Population_CEN_2010.sum()


##### 3) START AGGREGATING AND MERGING DATA
districts_merged = districts_unmerged

# This function will take a weighted column, group and sum up by district IDs, and merge it onto the districts dataset
def merge_column_into_districts_from_tract_data(col_name, districts_df):
    aggregated_series = overlap_tracts_merge.groupby("Leaid")[col_name].sum()
    new_df = districts_df.merge(pd.DataFrame(aggregated_series), left_on = "leaid11", right_index = True, how = "inner")
    return new_df

# This loop applies the function above to all the columns in the overlap dataset with weighted values 
for col in overlap_tracts_merge.columns:
    if "weighted_" in col:
        districts_merged = merge_column_into_districts_from_tract_data(col, districts_merged)

districts_merged
districts_merged.columns
districts_merged.shape

districts_merged.weighted_Tot_Housing_Units_CEN_2010.sum()
tracts.Tot_Housing_Units_CEN_2010.sum()

districts_merged.weighted_Tot_Population_CEN_2010.sum()
tracts.Tot_Population_CEN_2010.sum()

districts_merged.weighted_Tot_Occp_Units_ACS_08_12.sum()
overlap_tracts_merge.weighted_Tot_Occp_Units_ACS_08_12.sum()

districts_merged.index
districts_merged.leaid11

# This for loops correctly calculates median values because we can't calculate them merely by multiplying by percentage overlaps


for i in districts_merged.index:
    leaid = districts_merged.loc[i, "leaid11"]
    overlapping_tracts = overlap_tracts_merge[overlap_tracts_merge.Leaid == leaid]
    total_HH = districts_merged.loc[i, "weighted_Tot_Occp_Units_ACS_08_12"]
    
    med_income_list = overlapping_tracts.Med_HHD_Inc_ACS_08_12 * (overlapping_tracts.weighted_Tot_Occp_Units_ACS_08_12 / total_HH)
    med_value_list = overlapping_tracts.Med_House_value_ACS_08_12 * (overlapping_tracts.weighted_Tot_Occp_Units_ACS_08_12 / total_HH)
    
    med_income = sum(med_income_list[med_income_list.notnull()])   
    med_value = sum(med_value_list[med_value_list.notnull()])
    
    districts_merged.loc[i, "weighted_Med_HHD_Inc_ACS_08_12"] = med_income
    districts_merged.loc[i, "weighted_Med_House_value_ACS_08_12"] = med_value
    
districts_merged.weighted_Med_HHD_Inc_ACS_08_12.mean()
tracts.Med_HHD_Inc_ACS_08_12 = tracts.Med_HHD_Inc_ACS_08_12.apply(turn_dollars_into_float)
tracts.Med_HHD_Inc_ACS_08_12.mean()

districts_merged.weighted_Med_House_value_ACS_08_12.mean()
tracts.Med_House_value_ACS_08_12 = tracts.Med_House_value_ACS_08_12.apply(turn_dollars_into_float)
tracts.Med_House_value_ACS_08_12.mean()



# READ IN WEATHER DATA

weather = pd.read_csv("weather_temp_per_county.csv")
weather = weather[weather.Notes != "Total"] #get rid of duplicate cols
weather.columns

weather["avg_max_min_diff"] = weather['Avg Daily Max Air Temperature (F)'] - weather['Avg Daily Min Air Temperature (F)']

weather.columns

weather.rename(columns = {"Avg Daily Max Air Temperature (F)": "avg_of_daily_max",
                          "Min Temp for Daily Max Air Temp (F)": "min_of_daily_max",
                          "Max Temp for Daily Max Air Temp (F)": "max_of_daily_max",
                          "Avg Daily Min Air Temperature (F)": "avg_of_daily_min",
                          "Min Temp for Daily Min Air Temp (F)": "min_of_daily_min",
                          "Max Temp for Daily Min Air Temp (F)": "max_of_daily_min",
                          "County Code": "county_code"}, inplace = True)
                          

#need to concat state and county codes in grad rates

districts_merged.columns[20:45]

for i in districts_merged.index:
    county_code = districts_merged.loc[i, "County"].astype("string")
    state_code = districts_merged.loc[i, "State"].astype("string")

    if len(county_code) == 3:
        districts_merged.loc[i, "state_county_concat"] = int(state_code + county_code)
    elif len(county_code) == 2:
        districts_merged.loc[i, "state_county_concat"]= int(state_code + "0" + county_code)
    else:
        districts_merged.loc[i, "state_county_concat"] = int(state_code + "00" + county_code)


districts_merged.state_county_concat 
districts_merged = districts_merged.merge(weather, left_on = "state_county_concat", right_on = "county_code", how = "left")

districts_merged.columns


### MERGE IN FOOD DATA
 
food = pd.read_csv("food_access.csv")
food.columns
food.CensusTract # at the tract level...

overlap_for_food = overlap_tracts_merge[["GIDTR", "Leaid"]]

overlap_for_food_merged = overlap_for_food.merge(food, left_on = "GIDTR", right_on = "CensusTract", how = "left")

food_access_vars = ["LA1and10", "LA1and20", "LAhalfand10",
                    "LILATracts_1And10", "LILATracts_1And20",
                    "LILATracts_halfAnd10"]

testi = districts_merged.index[2]
test_leaid = districts_merged.loc[testi, 'leaid11']
test_leaid

for i, leaid in enumerate(districts_merged.leaid11):
    overlapping_tracts = overlap_for_food_merged[overlap_for_food_merged.Leaid == leaid]
    total_tracts = len(overlapping_tracts)
    
    for col in overlapping_tracts:
        if col in food_access_vars:
            low_income_tracts = sum(overlapping_tracts[col][overlapping_tracts[col].notnull()])
            percent_low_income_tracts = low_income_tracts * 100.0 / total_tracts
            
            districts_merged.loc[i, col] = percent_low_income_tracts
            


#Merge financials data

financials = pd.read_csv("school_financials.csv")

'''We need to merge the on the NCESID column (same as LEA ID), but it has some 
non-numeric observations. Need to investigate what those are.'''

non_int = []
for i, leaid in enumerate(financials.NCESID):
    try:
        int(leaid)
    except:
        non_int.append(i)
    
financials.iloc[non_int]["NAME"]
#seems like the non-numeric ones are kind of weird... let's drop them.

financials_w_integer_ids = financials.drop(financials.index[non_int])
financials_w_integer_ids.NCESID = financials_w_integer_ids.NCESID.astype("int")
    
districts_merged = districts_merged.merge(financials_w_integer_ids, how = "left", left_on = "leaid11", right_on = "NCESID")
districts_merged

#Rename financial columns 
districts_merged.rename(columns = {"PPSALWG": "tot_salaries_and_wages_per_pupil",
                             "PPEMPBEN": "tot_employee_benefits_per_pupil",
                             "PPITOTAL": "tot_instruction_spending_per_pupil",
                             "PPISALWG": "instruction_salaries_and_wages_per_pupil",
                             "PPIEMBEN": "instruction_benefits_per_pupil",
                             "PPSTOTAL": "support_spending_per_pupil",
                             "PPSPUPIL": "support_pupil_support_per_pupil",
                             "PPSSTAFF": "support_instructional_staff_per_pupil",
                             "PPSGENAD": "support_general_admin_per_pupil",
                             "PPSSCHAD": "support_school_admin_per_pupil",
                             "PCTFTOT": "pct_rev_from_federal",
                             "PCTFCOMP": "pct_rev_compensatory",
                             "PCTSTOT": "pct_rev_from_state",
                             "PCTSFORM": "pct_rev_general_formula_asst",
                             "PCTLTOT": "pct_rev_from_local",
                             "PCTLTAXP": "pct_rev_from_taxes_and_parent_contributions",
                             "PCTLOTHG": "pct_rev_from_other_local_govts",
                             "PCTLCHAR": "pct_rev_charges"}, inplace = True)
                             

grad_rates = districts_merged

### FEATURE ENGINEERING: CALCULATE NEEDED VARIABLES

#1) create dummy variables for States

grad_rates.STNAM = grad_rates.STNAM.astype("category")
state_dummies = pd.get_dummies(grad_rates.STNAM, prefix = "stnam")
state_dummies.iloc[:,1:] 
state_dummies = state_dummies.iloc[:,1:] #remove one of the dummies (Alabama)
len(state_dummies.columns)
grad_rates = pd.concat([grad_rates, state_dummies], axis = 1)

# 2) create variables for graduating cohort populations 

for col in grad_rates.columns:
    if "COHORT" in col:
        grad_rates[col] = grad_rates[col].fillna(0)

grad_rates["perc_ECD_in_cohort"] = grad_rates.ECD_COHORT_1112 * 100 / grad_rates.ALL_COHORT_1112
grad_rates["nat_amer_cohort_rate"] = (grad_rates.MAM_COHORT_1112 * 100.0) / grad_rates.ALL_COHORT_1112
grad_rates["asian_amer_cohort_rate"] = (grad_rates.MAS_COHORT_1112 * 100.0) / grad_rates.ALL_COHORT_1112
grad_rates["afr_amer_cohort_rate"] = (grad_rates.MBL_COHORT_1112 * 100.0) / grad_rates.ALL_COHORT_1112
grad_rates["hisp_cohort_rate"] = (grad_rates.MHI_COHORT_1112 * 100.0) / grad_rates.ALL_COHORT_1112
grad_rates["multirace_cohort_rate"] = (grad_rates.MTR_COHORT_1112 * 100.0) / grad_rates.ALL_COHORT_1112
grad_rates["white_cohort_rate"] = (grad_rates.MWH_COHORT_1112 * 100.0) / grad_rates.ALL_COHORT_1112
grad_rates["disability_cohort_rate"] = (grad_rates.CWD_COHORT_1112 * 100.0) / grad_rates.ALL_COHORT_1112
grad_rates["lim_eng_prof_cohort_rate"] = (grad_rates.LEP_COHORT_1112 * 100.0) / grad_rates.ALL_COHORT_1112


 # 3) Create urban population vars

grad_rates["pct_urban_pop"] = (grad_rates.weighted_URBANIZED_AREA_POP_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_urban_cluster_pop"] = (grad_rates.weighted_URBAN_CLUSTER_POP_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_rural_pop"] = (grad_rates.weighted_RURAL_POP_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Population_CEN_2010

# 4) Household vars

grad_rates["pct_occupied_HH"] = (grad_rates.weighted_Tot_Occp_Units_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Housing_Units_CEN_2010
grad_rates["pct_vacant_HH"] = (grad_rates.weighted_Tot_Vacant_Units_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Housing_Units_CEN_2010
              
grad_rates["pct_renter_occupied"] = (grad_rates.weighted_Renter_Occp_HU_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Occp_Units_CEN_2010
grad_rates["pct_owner_occupied"] = (grad_rates.weighted_Owner_Occp_HU_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Occp_Units_CEN_2010
                  
grad_rates["pct_people_with_different_HH_1yr_ago"] =  (grad_rates.weighted_Diff_HU_1yr_Ago_ACS_08_12 * 100.0) / grad_rates.weighted_Pop_1yr_Over_ACS_08_12
grad_rates["pct_HHs_where_householder_moved_in_2010"] = (grad_rates.weighted_HHD_Moved_in_ACS_08_12 * 100.0) / grad_rates.weighted_Tot_Occp_Units_ACS_08_12
             
grad_rates["pct_single_unit_HH"] = (grad_rates.weighted_Single_Unit_ACS_08_12 * 100.0) / grad_rates.weighted_Tot_Housing_Units_ACS_08_12
grad_rates["pct_multi_2to9_unit_HH"] = (grad_rates.weighted_MLT_U2_9_STRC_ACS_08_12 * 100.0) / grad_rates.weighted_Tot_Housing_Units_ACS_08_12
grad_rates["pct_multi_10p_unit_HH"] = (grad_rates.weighted_MLT_U10p_ACS_08_12 * 100.0) / grad_rates.weighted_Tot_Housing_Units_ACS_08_12
grad_rates["pct_mobile_HH"] = (grad_rates.weighted_Mobile_Homes_ACS_08_12 * 100.0) / grad_rates.weighted_Tot_Housing_Units_ACS_08_12

grad_rates["pct_crowded_occ"] = (grad_rates.weighted_Crowd_Occp_U_ACS_08_12 * 100.0) / grad_rates.weighted_Tot_Occp_Units_ACS_08_12
grad_rates["avg_occ"] = (grad_rates.weighted_Tot_Prns_in_HHD_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Occp_Units_CEN_2010
        
grad_rates["pct_female_only_HH"] = (grad_rates.weighted_Female_No_HB_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Occp_Units_CEN_2010
grad_rates["pct_married_HH"] = (grad_rates.weighted_MrdCple_Fmly_HHD_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Occp_Units_CEN_2010
grad_rates["pct_related_family_HH"] = (grad_rates.weighted_Rel_Family_HHDS_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Occp_Units_CEN_2010
grad_rates["pct_not_married_HH"] = (grad_rates.weighted_Not_MrdCple_HHD_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Occp_Units_CEN_2010
grad_rates["pct_nonfamily_HH"] = (grad_rates.weighted_NonFamily_HHD_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Occp_Units_CEN_2010
grad_rates["pct_single_person_HH"] = (grad_rates.weighted_Sngl_Prns_HHD_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Occp_Units_CEN_2010
grad_rates["pct_under18_HH"] = (grad_rates.weighted_HHD_PPL_Und_18_CEN_2010 * 100.0) / grad_rates.weighted_Tot_Occp_Units_CEN_2010
grad_rates["pct_related_under6_HH"] = (grad_rates.weighted_Rel_Child_Under_6_CEN_2010 * 100.0) / grad_rates.weighted_Rel_Family_HHDS_CEN_2010

# 5) Education Vars
grad_rates["pct_not_HS_grad"] = (grad_rates.weighted_Not_HS_Grad_ACS_08_12 * 100.0) / grad_rates.weighted_Pop_25yrs_Over_ACS_08_12
grad_rates["pct_HS_grad"] = 100.0 - grad_rates["pct_not_HS_grad"]
grad_rates["pct_college_grad"] = (grad_rates.weighted_College_ACS_08_12 * 100.0) / grad_rates.weighted_Pop_25yrs_Over_ACS_08_12

# 6) Poverty/public assistance/low income indicators 
grad_rates["pct_people_below_poverty"] = (grad_rates.weighted_Prs_Blw_Pov_Lev_ACS_08_12 * 100.0) / grad_rates.weighted_Pov_Univ_ACS_08_12
grad_rates["pct_HHs_with_public_asst_income"] = (grad_rates.weighted_PUB_ASST_INC_ACS_08_12 * 100.0) / grad_rates.weighted_Tot_Occp_Units_ACS_08_12
grad_rates["pct_HHs_without_plumbing"] = (grad_rates.weighted_No_Plumb_ACS_08_12 * 100.0) / grad_rates.weighted_Tot_Housing_Units_ACS_08_12
grad_rates["pct_HHs_without_phone"] = (grad_rates.weighted_Occp_U_NO_PH_SRVC_ACS_08_12 * 100.0) / grad_rates.weighted_Tot_Occp_Units_ACS_08_12

# 7) Labor variables
grad_rates["emp_rate_16p"] = (grad_rates.weighted_Civ_emp_16plus_ACS_08_12 * 100.0) / grad_rates.weighted_Civ_labor_16plus_ACS_08_12
grad_rates["emp_rate_16_24"] = (grad_rates.weighted_Civ_emp_16_24_ACS_08_12 * 100.0) / grad_rates.weighted_Civ_labor_16_24_ACS_08_12
grad_rates["emp_rate_25_44"] = (grad_rates.weighted_Civ_emp_25_44_ACS_08_12 * 100.0) / grad_rates.weighted_Civ_labor_25_44_ACS_08_12
grad_rates["emp_rate_45_64"] = (grad_rates.weighted_Civ_emp_45_64_ACS_08_12 * 100.0) / grad_rates.weighted_Civ_labor_45_64_ACS_08_12
grad_rates["emp_rate_65p"] = (grad_rates.weighted_Civ_emp_65plus_ACS_08_12 * 100.0) / grad_rates.weighted_Civ_labor_65plus_ACS_08_12

# 8) Lanugage vars
grad_rates["pct_other_language_at_home"] = (grad_rates.weighted_Othr_Lang_ACS_08_12 * 100.0) / grad_rates.weighted_Pop_5yrs_Over_ACS_08_12
grad_rates["pct_only_english"] = (grad_rates.weighted_Age5p_Only_English_ACS_08_12 * 100.0) / grad_rates.weighted_Pop_5yrs_Over_ACS_08_12

# 9) Demographic vars
grad_rates["pct_male"] = grad_rates.weighted_Males_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_female"] = grad_rates.weighted_Females_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010

grad_rates["pct_age_under5"] = grad_rates.weighted_Pop_under_5_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_age_5to17"] = grad_rates.weighted_Pop_5_17_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_age_18to24"] = grad_rates.weighted_Pop_18_24_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_age_25to44"] = grad_rates.weighted_Pop_25_44_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_age_45to64"] = grad_rates.weighted_Pop_45_64_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_age_65p"] = grad_rates.weighted_Pop_65plus_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_hispanic"] = grad_rates.weighted_Hispanic_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_NH_white_only"] = grad_rates.weighted_NH_White_alone_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_black_only"] = grad_rates.weighted_NH_Blk_alone_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_AIAN_only"] = grad_rates.weighted_NH_AIAN_alone_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_Asian_only"] = grad_rates.weighted_NH_Asian_alone_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_NHOPI_only"] = grad_rates.weighted_NH_NHOPI_alone_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_SOR_only"] = grad_rates.weighted_NH_SOR_alone_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010

# 10) Group instituion vars
grad_rates["pct_group_quarters"] = grad_rates.weighted_Tot_GQ_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_institutionalized_group_quarters"] = grad_rates.weighted_Inst_GQ_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010
grad_rates["pct_non_institutionalized_group_quarters"] = grad_rates.weighted_Non_Inst_GQ_CEN_2010 * 100.00 / grad_rates.weighted_Tot_Population_CEN_2010

# 11) Citizenship and country of origin vars

grad_rates["pct_US_born"] = grad_rates.weighted_Born_US_ACS_08_12 * 100.0 / grad_rates.weighted_Tot_Population_ACS_08_12
grad_rates["pct_foreign_born"] = grad_rates.weighted_Born_foreign_ACS_08_12 * 100.0 / grad_rates.weighted_Tot_Population_ACS_08_12
grad_rates["pct_naturalized_citizens"] = grad_rates.weighted_US_Cit_Nat_ACS_08_12 * 100.0 / grad_rates.weighted_Tot_Population_ACS_08_12
grad_rates["pct_not_citizens"] = grad_rates.weighted_NON_US_Cit_ACS_08_12 * 100.0 / grad_rates.weighted_Tot_Population_ACS_08_12


               
# WRITE MERGED CSV
grad_rates.to_csv("merged_and_weighted_data.csv")



