# -*- coding: utf-8 -*-
"""
Created on Mon Nov 16 16:26:15 2015

@author: asjedh
"""


import pandas as pd
import os
import numpy as np
from sklearn.linear_model import LinearRegression 
import statsmodels.formula.api as sm
from statsmodels.tools.tools import add_constant
from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import cross_val_score
from sklearn.cross_validation import train_test_split
from sklearn.grid_search import GridSearchCV
from random import randint
import random
import seaborn as sb


os.chdir("/Users/asjedh/Desktop/DataForDiploma/data")

grad_rates = pd.read_csv("merged_and_weighted_data.csv")

grad_rates_200p = grad_rates[grad_rates.ALL_COHORT_1112 > 200]

def create_clean_inputs(X_cols_list, y_col_string, df):
    cols = X_cols_list + [y_col_string]
    df_inputs_dropped_null = df[cols].dropna()
    
    return df_inputs_dropped_null[X_cols_list], df_inputs_dropped_null[y_col_string]

simplified_vars = ["perc_ECD_in_cohort", "pct_not_married_HH", "pct_female_only_HH", 
                   "pct_people_below_poverty", "instruction_salaries_and_wages_per_pupil",
                   "avg_of_daily_min", "avg_of_daily_max"]
                   
rf_200p = RandomForestRegressor(n_estimators = 300, random_state = 1, oob_score=True)
X, y = create_clean_inputs(simplified_vars, "clean_grad_rate", grad_rates_200p)
rf_200p.fit(X, y)

rf_200p.predict(grad_rates_200p)


def predict_national_grad_rate_for_percent_change_in_feature(feature, percent_change, df, model, vars_for_model):
    total_students = df[df[vars_for_model].notnull().all(axis = 1)].ALL_COHORT_1112.sum()
    graduating_students = []
    
    for index, district in df.iterrows():
        if district[vars_for_model].isnull().any().any():
            next
        else:
            district_copy = district.copy()
            district_copy[feature] =  district_copy[feature] * (1 + percent_change)
            
            predicted_grad_rate = model.predict(district_copy[vars_for_model])
            predicted_number_of_graduating_students = predicted_grad_rate * district_copy.ALL_COHORT_1112
            
            graduating_students.append(predicted_number_of_graduating_students)
    
    national_grad_rate = (sum(graduating_students) / total_students)[0]
    return national_grad_rate        


def get_graph_data_for_changes_in_feature(feature, df, model, vars_for_model):
    percent_changes = [-.5, -.45, -.40, -.35, -.30, -.25, -.20, -.15, -.1, -.05, 0,
                       .05, .10, .15, .20, .25, .30, .35, .40, .45, .50]
                     
    predicted_national_graduation_rates = []
    for change in percent_changes:
        predicted = predict_national_grad_rate_for_percent_change_in_feature(feature, change, df,
                                                                             model, vars_for_model)
        
        predicted_national_graduation_rates.append(predicted)
    
    percent_changes = ["{}%".format(int(change * 100)) for change in percent_changes]

    graph_data = pd.DataFrame({"Percent Changes in Feature": percent_changes,
                               "Predicted National Graduation Rate": predicted_national_graduation_rates})
                               
    return graph_data
                                                                            


os.chdir("/Users/asjedh/Desktop/DataForDiploma/files_needed_for_notebook/data")


# ECD students in cohort spending, entire dataset
ecd_students_change_effect = get_graph_data_for_changes_in_feature("perc_ECD_in_cohort", grad_rates_200p, rf_200p, simplified_vars)
ecd_students_change_effect.to_csv("ecd_students_change_effect.csv")
ecd_students_change_effect.plot(x = "Percent Changes in Feature", y = "Predicted National Graduation Rate")

# female householder only households, entire dataset
female_only_householder_change_effect = get_graph_data_for_changes_in_feature("pct_female_only_HH", grad_rates_200p, rf_200p, simplified_vars)
female_only_householder_change_effect.to_csv("female_only_householder_change_effect.csv")
female_only_householder_change_effect.plot(x = "Percent Changes in Feature", y = "Predicted National Graduation Rate")

# unmarried households, entire dataset
unmarried_households_change_effect = get_graph_data_for_changes_in_feature("pct_not_married_HH", grad_rates_200p, rf_200p, simplified_vars)
unmarried_households_change_effect.to_csv("unmarried_households_change_effect.csv")
unmarried_households_change_effect.plot(x = "Percent Changes in Feature", y = "Predicted National Graduation Rate")

# people below poverty line, entire dataset
ppl_below_poverty_line_change_effect = get_graph_data_for_changes_in_feature("pct_people_below_poverty", grad_rates_200p, rf_200p, simplified_vars)
ppl_below_poverty_line_change_effect.to_csv("ppl_below_poverty_line_change_effect.csv")
ppl_below_poverty_line_change_effect.plot(x = "Percent Changes in Feature", y = "Predicted National Graduation Rate")

# instruction spending in cohort, entire dataset
instruction_spending_change_effect = get_graph_data_for_changes_in_feature("instruction_salaries_and_wages_per_pupil", grad_rates_200p, rf_200p, simplified_vars)
instruction_spending_change_effect.to_csv("instruction_spending_change_effect.csv")
instruction_spending_change_effect.plot(x = "Percent Changes in Feature", y = "Predicted National Graduation Rate")

# daily max change effect, entire dataset
daily_max_change_effect = get_graph_data_for_changes_in_feature("avg_of_daily_max", grad_rates_200p, rf_200p, simplified_vars)
daily_max_change_effect.to_csv("daily_max_change_effect.csv")
daily_max_change_effect.plot(x = "Percent Changes in Feature", y = "Predicted National Graduation Rate")

# daily min change effect, entire dataset
daily_min_change_effect = get_graph_data_for_changes_in_feature("avg_of_daily_min", grad_rates_200p, rf_200p, simplified_vars)
daily_min_change_effect.to_csv("daily_min_change_effect.csv")
daily_min_change_effect.plot(x = "Percent Changes in Feature", y = "Predicted National Graduation Rate")

