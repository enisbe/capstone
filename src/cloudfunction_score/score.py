import pandas as pd
from datetime import datetime, timedelta
import json
import requests
import path as path 
import config
import cloud_storage as storage

def score():
    print("\t|--Getting Data.")
    full_df = storage.load_data(path.final_data)
    old_prediction = storage.load_data(path.test_prediction)
    
    if config.cloud_prediction_engine:
        url = "https://container-deploy.uc.r.appspot.com/predict24"
    else:
        url = "http://localhost:8080/predict24"

    testing_dates = {}
    most_recent_date = full_df['Dates'].max()

    testing_dates  = {'cv_start': '2010-10-01', 
                       'cv_end': '2021-07-01', 
                        'pred_start': '2021-08-01',
                        'pred_end': most_recent_date}


    feature_names = ['Payrolls_3mo_vs_12mo',
                          'Real_Fed_Funds_Rate_12mo_chg',
                          'CPI_3mo_pct_chg_annualized',
                          '10Y_Treasury_Rate_12mo_chg',
                          '3M_10Y_Treasury_Spread',
                          'S&P_500_12mo_chg']
    output_names = ['Recession','Recession_within_6mo',  'Recession_within_12mo', 'Recession_within_24mo']

    print("\t|--prepared for scoring.")

    full_df = full_df.sort_values(['Dates'], ascending=True)
    full_df.reset_index(inplace=True)
    full_df.drop('index', axis=1, inplace=True)
    date_condition = ((full_df['Dates'] <= testing_dates['pred_end']) &
                      (full_df['Dates'] >= testing_dates['pred_start']))
    pred_indices = list(full_df[date_condition].index)
    testing_x = full_df[['Dates']+feature_names].loc[pred_indices]

    print(f"\t|--Create payload and score using {url}.")

    # Make Json payload and make prediction
    json_payload = json.loads(testing_x.to_json())
    r = requests.post(url, json=json_payload)
    results = dict(r.json())

    print(f"\t|--process results.")

    #Process Results
    mods = ['6mo', '12mo', '24mo']
    names = {
            "6mo": "Recession_within_6mo",
             "12mo": "Recession_within_12mo",
             "24mo": "Recession_within_24mo"
            }

    for k,v  in names.items():
        if k == '6mo':
            df = pd.DataFrame({"Dates": results[k]['Dates'], names[k]: results[k]['prediction']})
        else:
            df = df.join( pd.DataFrame({  names[k]: results[k]['prediction']}) )

    indicators = list(names.values())

    full_df_ind = full_df[['Dates', 'Recession'] + indicators]  
    full_df_ind.columns = ['Dates', 'True_Recession'] + ["True_" + f for f in indicators]

    df.columns = ['Dates'] + ["Pred_" + f for f in indicators]

    # Merge and create final Results
    new_pred = full_df_ind.merge(df, on='Dates')

    columns = ['Dates',
     'True_Recession',
     'True_Recession_within_6mo',
     'Pred_Recession_within_6mo',
     'True_Recession_within_12mo',
     'Pred_Recession_within_12mo',
     'True_Recession_within_24mo',
     'Pred_Recession_within_24mo']

    new_pred = new_pred[columns]

    print(f"\t|--Save Data.")

    final_pred = pd.concat([ old_prediction[old_prediction['Dates'] <new_pred['Dates'].min()], new_pred])
    final_pred.reset_index(drop=True,inplace=True)
    storage.save_data(final_pred, path.test_prediction)
    
 