# from src.data_utils import DataSeries
# from src.data_utils import YahooData
import  path as path
import config as config
import pandas as pd
import cloud_storage as storage


from datetime import datetime, timedelta
import re
from io import StringIO
import json
from datetime import datetime, timedelta
import requests as req
import pandas as pd
import numpy as np
import  data_util  
import secrets
import requests as req



fred_series_ids = {'Non-farm_Payrolls': 'PAYEMS',
                        'Civilian_Unemployment_Rate': 'UNRATE',
                        'Effective_Fed_Funds': 'FEDFUNDS',
                        'CPI_All_Items': 'CPIAUCSL',
                        '10Y_Treasury_Rate': 'GS10',
                        '5Y_Treasury_Rate': 'GS5',
                        '3_Month_T-Bill_Rate': 'TB3MS',
                        'IPI': 'INDPRO'}
yahoo_series_ids = {'S&P_500_Index': '^GSPC'}

primary_df_output = pd.DataFrame()
primary_df_output_stale = pd.DataFrame()
primary_dictionary_output ={}
shortest_series_name = ''
shortest_series_length = 1000000
 
    

def get_yahoo_data():
    print('|--Getting Yahoo Finance Data--')

    for series_name in list(yahoo_series_ids.keys()):
        series_data = data_util.DataSeries()
        series_id = yahoo_series_ids[series_name]
        print('\t|--Getting data for {}({}).'.format(series_name, series_id))
        success = False
        while success == False:
            try:
                series_data.yahoo_response(series_id)
            except req.HTTPError:
                delay = 5
                print('\t --CONNECTION ERROR--',
                      '\n\t Sleeping for {} seconds.'.format(delay))
                time.sleep(delay)
            else:
                success = True
        primary_dictionary_output[series_name] = series_data
    print('Finished getting data from Yahoo Finance!')

    
    
def get_fred_data():
    print('|--Getting FRED Data--')    
    
    # FRED Data will update after the 8th. Between 1 and 8 it will throw an error.
    # if day is before 8 then simply pull in the last month numbers
    
    now = datetime.now() 
    if now.day < 8:
        now = datetime.today().replace(day=1) - timedelta(1)

    
    month = now.strftime('%m')
    year = now.year    
 
    most_recent_date = '{}-{}-08'.format(year, month)
    for series_name in list(fred_series_ids.keys()):
        series_data = data_util.DataSeries()
        series_id = fred_series_ids[series_name]
        print('\t|--Getting data for {}({}){}.'.format(series_name, series_id, most_recent_date))
        params = {'series_id': series_id,
                  'series_name': series_name,
                  'api_key': secrets.api_key,              
                  'file_type': 'json',
                  'sort_order': 'desc',
                  'realtime_start': most_recent_date,
                  'realtime_end': most_recent_date}
        success = False 
        while success == False:
            try:
                series_data.fred_response(params)
            except json.JSONDecodeError:
                delay = 5
                print('\t --CONNECTION ERROR--',
                      '\n\t Sleeping for {} seconds.'.format(delay))
                time.sleep(delay) 
            else:
                success = True
        primary_dictionary_output[series_name] = series_data
  


def fix_s500(): # yahoo_data_sp500_fix
    """
    For some reason Yahoo Finance is no longer providing monthly
    S&P 500 data past the cutoff_date. So will need to retrieve all
    S&P 500 data prior to cutoff_date from a previous run of the code.
    My Comment: Basically everything before 1985 is missing so he got custom series from somewhere and append that to dataseries
    """
    if config.read_cloud:
        sp500_precutoff_data =storage.load_cloud(path.sp500_precutoff_data)
    else:
        sp500_precutoff_data = storage.load_local(path.dir_path + path.sp500_precutoff_data)
    
 
    sp500_precutoff_data.sort_index(inplace=True)
    cutoff_date = primary_dictionary_output['S&P_500_Index'].dates[::-1][0]
    cutoff_date_mask = sp500_precutoff_data.loc[:,'Dates'] < cutoff_date
    primary_dictionary_output['S&P_500_Index'].dates.extend(sp500_precutoff_data.loc[cutoff_date_mask, 'Dates'])
    primary_dictionary_output['S&P_500_Index'].values.extend(sp500_precutoff_data.loc[cutoff_date_mask, 'S&P_500_Index'])
        
        
        
def find_shortest_series():
    global shortest_series_length,shortest_series_name
 
    for series_name in primary_dictionary_output.keys():
        series_data = primary_dictionary_output[series_name]
        if len(series_data.dates) < shortest_series_length:
            shortest_series_length = len(series_data.dates)
            shortest_series_name = series_name

            
            
def combine_data():
    global primary_df_output, primary_df_output_stale
    print('|--Combining primary dataset...')
    now = datetime.now()
    if now.day < 8:
        now = datetime.today().replace(day=1) - timedelta(1)

    current_month = int(now.strftime('%m'))
    current_year = now.year        

    dates = []
    for months_ago in range(0, shortest_series_length):
        if current_month < 10:
            dates.append('{}-0{}-01'.format(current_year, current_month))
        else:
            dates.append('{}-{}-01'.format(current_year, current_month))

        if current_month == 1:
            current_month = 12
            current_year -= 1
        else:
            current_month -= 1

    primary_df_output['Dates'] = dates

    for series_name in primary_dictionary_output.keys():
        if series_name != 'S&P_500_Index':
            
            series_data = primary_dictionary_output[series_name]
            primary_df_output[series_name] = series_data.values[:shortest_series_length]
        else:
            series_data = primary_dictionary_output[series_name]
            sp500 = pd.DataFrame({"Dates": series_data.dates, "S&P_500_Index": series_data.values } )
            primary_df_output = primary_df_output.merge(sp500, how='outer') # pd.concat([primary_df_output.set_index('Dates') ,s],axis=1)
             
    primary_df_output.sort_values("Dates", ascending=False, inplace=True)
    
    mask = primary_df_output.iloc[:,1:].isna().all(axis=1)
    primary_df_output = primary_df_output[~mask]
    
    primary_df_output_stale = pd.DataFrame( np.where(primary_df_output.isna(),1,0))
    primary_df_output_stale.columns = primary_df_output.columns
    
    primary_df_output.bfill(inplace=True)
    primary_df_output.reset_index(drop=True,inplace=True)
    print('\t|--Finished combining primary dataset!')
    
    
    
def update_data(update_month_history=3):
    """
    This function updates the old data and make the update old data primary data. 
    We download the entire data set from FRED. Then we look at the old data 
    and add new rows (month) to old data. Then we update the old data with new
    infromation that has changes (e.g. SP500 changes daily). 
    THe reason to it this way as opose to overwriting is because I want to gurantaee then we have the old data as 
    history so that doesnt changes.
    """
    print("|--updating old data while keeping history..")
    global primary_df_output
    
    if config.read_cloud:
        old_data =storage.load_cloud(path.latest_data)
    else:
        old_data = storage.load_local(path.dir_path + path.latest_data)
        
    new_dates = np.setdiff1d(primary_df_output.Dates, old_data.Dates).tolist()
    new_data_points = primary_df_output[primary_df_output['Dates'].isin(new_dates)]
    updated_data = pd.concat([new_data_points, old_data]).sort_values("Dates",ascending=False).reset_index(drop=True)

    # update the data differences where they exist this is mostly related to SP500 prices
    print("\t|--Updating {}--".format(update_month_history))
 
    diff = updated_data.iloc[:update_month_history,:] ==primary_df_output.iloc[:update_month_history,:]

    idx = diff[(~diff.all(axis=1))].index
 
    updated_data.loc[idx,:] = primary_df_output.loc[idx,:] 
    primary_df_output = updated_data
    print("\t|--updating finished--")

 