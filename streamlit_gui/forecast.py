import pandas as pd
import numpy as np
import json
import requests
 
url = "https://container-deploy.uc.r.appspot.com/predict24"

def process_data(df):
    # Payrol 3 mo vs 12 months change annulized
    needed =['Dates', 'Non-farm_Payrolls','Effective_Fed_Funds','CPI_All_Items','10Y_Treasury_Rate','3_Month_T-Bill_Rate','S&P_500_Index']
    if len(set(needed) - set(df.columns)) > 0:
        raise ValueError(f"Mssing Columns. You need {str(needed)} columns")
    df1 = df.sort_values('Dates', ascending= False).copy()
    df1['payrolls_3mo'] =    ((df1['Non-farm_Payrolls'].shift(0)/df1['Non-farm_Payrolls'].shift(-3))**4)-1
    df1['payrolls_12mo'] =    ((df1['Non-farm_Payrolls'].shift(0)/df1['Non-farm_Payrolls'].shift(-12)))-1
    df1['Payrolls_3mo_vs_12mo']  = df1['payrolls_3mo'] - df1['payrolls_12mo'] 
 
    df1['Real_Fed_Funds_Rate_12mo_chg']  = df1['Effective_Fed_Funds'].shift(0) - df1['Effective_Fed_Funds'].shift(-12)
    df1['CPI_3mo_pct_chg_annualized'] = ((df1['CPI_All_Items'].shift(0) / df1['CPI_All_Items'].shift(-3))**4)-1
 
    df1['10Y_Treasury_Rate_12mo_chg'] = df1['10Y_Treasury_Rate'].shift(0) - df1['10Y_Treasury_Rate'].shift(-12)
    
    df1['3M_10Y_Treasury_Spread'] = df1['10Y_Treasury_Rate'].shift(0) - df1['3_Month_T-Bill_Rate'].shift(0)
    df1['S&P_500_12mo_chg'] =   df1 ['S&P_500_Index']/ df1['S&P_500_Index'].shift(-12) - 1
    
    return df1[['Dates', 'Payrolls_3mo_vs_12mo','Real_Fed_Funds_Rate_12mo_chg','CPI_3mo_pct_chg_annualized',
                '10Y_Treasury_Rate_12mo_chg','3M_10Y_Treasury_Spread','S&P_500_12mo_chg']]



def prediction(forecast, df_raw,  df_final, df_pred):
    

    
    end_date_actual = pd.to_datetime(df_raw['Dates'].max())
    
    # f is the forecast only after the end_of_actual
    f = forecast[pd.to_datetime(forecast['Dates']) > end_date_actual]
    f.loc[:,'Dates'] = pd.to_datetime(f['Dates']).dt.strftime("%Y-%m-%d") 
    forecast_begin = f['Dates'].min()

    df_raw_plus_forecast = pd.concat([df_raw, f], axis=0).sort_values(by='Dates')
    
    forecast_variables = process_data(pd.concat([df_raw,f],axis=0))

    testing_x = forecast_variables[forecast_variables['Dates'] > df_raw['Dates'].max()].sort_values( by='Dates')
    # testing_x
    json_payload = json.loads(testing_x.to_json())
    r = requests.post(url, json=json_payload)
    results = dict(r.json())
    #Process Results
    mods = ['6mo', '12mo', '24mo']
    names = {
            "6mo": "Recession_within_6mo",
             "12mo": "Recession_within_12mo",
             "24mo": "Recession_within_24mo"
            }
    for k,v  in names.items():
        if k == '6mo': # for first k we create data frame for (first k happens to be "6mo"
            df = pd.DataFrame({"Dates": results[k]['Dates'], names[k]: results[k]['prediction']})
        else:
            df = df.join( pd.DataFrame({  names[k]: results[k]['prediction']}) )

    indicators = list(names.values())

    full_df_ind = df_final[['Dates', 'Recession'] + indicators]  
    full_df_ind.columns = ['Dates', 'True_Recession'] + ["True_" + f for f in indicators]

    df.columns = ['Dates'] + ["Pred_" + f for f in indicators]
    # Merge and create final Results
    new_pred = full_df_ind.merge(df, on='Dates', how='right')

    columns = ['Dates',
     'True_Recession',
     'True_Recession_within_6mo',
     'Pred_Recession_within_6mo',
     'True_Recession_within_12mo',
     'Pred_Recession_within_12mo',
     'True_Recession_within_24mo',
     'Pred_Recession_within_24mo']

    new_pred = new_pred[columns]
    new_pred = new_pred.fillna(0) # I am filling NA becuase I don have filled recession Actual flags filled in. This is hopefully be done through the real datda.
    final_pred = pd.concat([ df_pred[df_pred['Dates'] <new_pred['Dates'].min()], new_pred])
    final_pred.reset_index(drop=True,inplace=True)
    
    return final_pred, forecast_variables, df_raw_plus_forecast, forecast_begin
    