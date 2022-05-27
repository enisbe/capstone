import path as path
import config as config
import pandas as pd
from datetime import datetime, timedelta
import re
from io import StringIO
import json
from datetime import datetime, timedelta
import requests as req
import pandas as pd
import numpy as np

 


def calculate_secondary_data(primary_df_output):
        """
        Builds some features from the primary dataset to create a secondary
        dataset.
        """
        # global secondary_df_output  
   
        dates = []
        payrolls_3mo = []
        payrolls_12mo = []
        unemployment_rate = []
        unemployment_rate_12mo_chg = []
        real_fed_funds = []
        real_fed_funds_12mo = []
        CPI_3mo = []
        CPI_12mo = []
        treasury_10Y_12mo = []
        treasury_3M_12mo = []
        treasury_10Y_3M_spread = []
        treasury_10Y_5Y_spread = []
        treasury_10Y_3M_spread_12mo = []
        sp_500_3mo = []
        sp_500_12mo = []
        IPI_3mo = []
        IPI_12mo = []
        
        for index in range(0, len(primary_df_output) - 12):
            dates.append(primary_df_output['Dates'][index])
            payrolls_3mo_pct_chg = (primary_df_output['Non-farm_Payrolls'][index]/ primary_df_output['Non-farm_Payrolls'][index + 3]) - 1
            payrolls_3mo.append(((1 + payrolls_3mo_pct_chg) ** 4) - 1)
            payrolls_12mo.append((primary_df_output['Non-farm_Payrolls'][index]/ primary_df_output['Non-farm_Payrolls'][index + 12]) - 1)
            unemployment_rate.append(primary_df_output['Civilian_Unemployment_Rate'][index])
            unemployment_rate_12mo_chg.append((primary_df_output['Civilian_Unemployment_Rate'][index])- primary_df_output['Civilian_Unemployment_Rate'][index + 12])
            CPI_3mo_pct_chg = (primary_df_output['CPI_All_Items'][index]
                / primary_df_output['CPI_All_Items'][index + 3]) - 1
            CPI_3mo.append(((1 + CPI_3mo_pct_chg) ** 4) - 1)
            CPI_12mo_pct_chg = (primary_df_output['CPI_All_Items'][index]
                / primary_df_output['CPI_All_Items'][index + 12]) - 1
            CPI_12mo.append(CPI_12mo_pct_chg)
            real_fed_funds.append(primary_df_output['Effective_Fed_Funds'][index]
                - (CPI_12mo_pct_chg * 100))
            real_fed_funds_12mo.append(primary_df_output['Effective_Fed_Funds'][index]
                - primary_df_output['Effective_Fed_Funds'][index + 12])
            treasury_10Y_12mo.append(primary_df_output['10Y_Treasury_Rate'][index]
                - primary_df_output['10Y_Treasury_Rate'][index + 12])
            treasury_3M_12mo.append(primary_df_output['3_Month_T-Bill_Rate'][index]
                - primary_df_output['3_Month_T-Bill_Rate'][index + 12])
            treasury_10Y_3M_spread_today = (primary_df_output['10Y_Treasury_Rate'][index]
                - primary_df_output['3_Month_T-Bill_Rate'][index])
            treasury_10Y_3M_spread.append(treasury_10Y_3M_spread_today)
            treasury_10Y_3M_spread_12mo_ago = (primary_df_output['10Y_Treasury_Rate'][index + 12]
                - primary_df_output['3_Month_T-Bill_Rate'][index + 12])
            treasury_10Y_3M_spread_12mo.append(treasury_10Y_3M_spread_today
                                               - treasury_10Y_3M_spread_12mo_ago)
            treasury_10Y_5Y_spread_today = (primary_df_output['10Y_Treasury_Rate'][index]
                - primary_df_output['5Y_Treasury_Rate'][index])
            treasury_10Y_5Y_spread.append(treasury_10Y_5Y_spread_today)
            sp_500_3mo.append((primary_df_output['S&P_500_Index'][index]
                / primary_df_output['S&P_500_Index'][index + 3]) - 1)
            sp_500_12mo.append((primary_df_output['S&P_500_Index'][index]
                / primary_df_output['S&P_500_Index'][index +12]) - 1)
            IPI_3mo_pct_chg = (primary_df_output['IPI'][index]
                / primary_df_output['IPI'][index + 3]) - 1
            IPI_3mo.append(((1 + IPI_3mo_pct_chg) ** 4) - 1)
            IPI_12mo_pct_chg = (primary_df_output['IPI'][index]
                / primary_df_output['IPI'][index + 12]) - 1
            IPI_12mo.append(IPI_12mo_pct_chg)
            
        secondary_df_output = pd.DataFrame({
                'Dates': dates,
                'Payrolls_3mo_pct_chg_annualized': payrolls_3mo,
                'Payrolls_12mo_pct_chg': payrolls_12mo,
                'Unemployment_Rate': unemployment_rate,
                'Unemployment_Rate_12mo_chg': unemployment_rate_12mo_chg,
                'Real_Fed_Funds_Rate': real_fed_funds,
                'Real_Fed_Funds_Rate_12mo_chg': real_fed_funds_12mo,
                'CPI_3mo_pct_chg_annualized': CPI_3mo,
                'CPI_12mo_pct_chg': CPI_12mo,
                '10Y_Treasury_Rate_12mo_chg': treasury_10Y_12mo,
                '3M_Treasury_Rate_12mo_chg': treasury_3M_12mo,
                '3M_10Y_Treasury_Spread': treasury_10Y_3M_spread,
                '3M_10Y_Treasury_Spread_12mo_chg': treasury_10Y_3M_spread_12mo,
                '5Y_10Y_Treasury_Spread': treasury_10Y_5Y_spread,
                'S&P_500_3mo_chg': sp_500_3mo,
                'S&P_500_12mo_chg': sp_500_12mo,
                'IPI_3mo_pct_chg_annualized': IPI_3mo,
                'IPI_12mo_pct_chg': IPI_12mo})
        return secondary_df_output

        
def make_features(secondary_df_output):
    """
    Creates additional features, and adds them to the final dataframe.
    """
    # global final_df_output, secondary_df_output
    payrolls_3mo_vs_12mo = (secondary_df_output['Payrolls_3mo_pct_chg_annualized']
        - secondary_df_output['Payrolls_12mo_pct_chg'])
    CPI_3mo_vs_12mo = (secondary_df_output['CPI_3mo_pct_chg_annualized']
        - secondary_df_output['CPI_12mo_pct_chg'])
    sp500_3mo_vs_12mo = (secondary_df_output['S&P_500_3mo_chg']
        - secondary_df_output['S&P_500_12mo_chg'])
    IPI_3mo_vs_12mo = (secondary_df_output['IPI_3mo_pct_chg_annualized']
        - secondary_df_output['IPI_12mo_pct_chg'])

    secondary_df_output['Payrolls_3mo_vs_12mo'] = payrolls_3mo_vs_12mo
    secondary_df_output['CPI_3mo_vs_12mo'] = CPI_3mo_vs_12mo
    secondary_df_output['S&P_500_3mo_vs_12mo'] = sp500_3mo_vs_12mo
    secondary_df_output['IPI_3mo_vs_12mo'] = IPI_3mo_vs_12mo
    return secondary_df_output
    
    
def label_output(final_df_output):
    """
    Labels the various outputs.
    """
 

    NBER_recessions = {'1': {'Begin': '1957-09-01', 'End': '1958-04-01'},
                       '2': {'Begin': '1960-05-01', 'End': '1961-02-01'},
                       '3': {'Begin': '1970-01-01', 'End': '1970-11-01'},
                       '4': {'Begin': '1973-12-01', 'End': '1975-03-01'},
                       '5': {'Begin': '1980-02-01', 'End': '1980-07-01'},
                       '6': {'Begin': '1981-08-01', 'End': '1982-11-01'},
                       '7': {'Begin': '1990-08-01', 'End': '1991-03-01'},
                       '8': {'Begin': '2001-04-01', 'End': '2001-11-01'},
                       '9': {'Begin': '2008-01-01', 'End': '2009-06-01'},
                       '10': {'Begin': '2020-03-01', 'End': '2020-04-01'}}

    observation_count = len(final_df_output)
    final_df_output['Recession'] = [0] * observation_count
    final_df_output['Recession_in_6mo'] = [0] * observation_count
    final_df_output['Recession_in_12mo'] = [0] * observation_count
    final_df_output['Recession_in_24mo'] = [0] * observation_count
    final_df_output['Recession_within_6mo'] = [0] * observation_count
    final_df_output['Recession_within_12mo'] = [0] * observation_count
    final_df_output['Recession_within_24mo'] = [0] * observation_count

    for recession in NBER_recessions:
        end_condition = (NBER_recessions[recession]['End'] >= final_df_output['Dates'])
        begin_condition = (final_df_output['Dates'] >= NBER_recessions[recession]['Begin'])
        final_df_output.loc[end_condition & begin_condition, 'Recession'] = 1

    for index in range(0, len(final_df_output)):
        if final_df_output['Recession'][index] == 1:
            final_df_output.loc[min(index + 6, len(final_df_output) - 1), 'Recession_in_6mo'] = 1
            final_df_output.loc[min(index + 12, len(final_df_output) - 1), 'Recession_in_12mo'] = 1
            final_df_output.loc[min(index + 24, len(final_df_output) - 1), 'Recession_in_24mo'] = 1
            final_df_output.loc[index : min(index + 6, len(final_df_output) - 1), 'Recession_within_6mo'] = 1
            final_df_output.loc[index : min(index + 12, len(final_df_output) - 1), 'Recession_within_12mo'] = 1
            final_df_output.loc[index : min(index + 24, len(final_df_output) - 1), 'Recession_within_24mo'] = 1
    return final_df_output


# def load_primary_data():
#     primary_df_output = pd.read_csv(path.dir_path + path.latest_data)
#     return primary_df_output


def create_secondary_data(primary_df_output):
    print('\n|--Creating secondary dataset from "latest_data.csv"')
    primary_df_output.sort_index(inplace=True)
    df =  calculate_secondary_data(primary_df_output)
    print('\t|--Finished creating secondary dataset!')
    return df

    
def save_secondary_data(primary_df_output):    
    secondary_df_output.to_csv(path.latest_secondary_data, index=False)
    
    
def load_secondary_data():
    latest_secondary_data = pd.read_csv(path.latest_secondary_data)
    return latest_secondary_data

    
def create_final_data(secondary_df_output):
    print('|--Creating final dataset from "latest_secondary_data.csv"')
    final_df_output = secondary_df_output
    # return final_df_output
    final_df_output = make_features(final_df_output)
    # return final_df_output
    final_df_output = label_output(final_df_output)
    new_cols = ['Dates', 'Recession', 'Recession_in_6mo',
                'Recession_in_12mo', 'Recession_in_24mo',
                'Recession_within_6mo', 'Recession_within_12mo',
                'Recession_within_24mo', 'Payrolls_3mo_pct_chg_annualized',
                'Payrolls_12mo_pct_chg', 'Payrolls_3mo_vs_12mo',
                'Unemployment_Rate', 'Unemployment_Rate_12mo_chg',
                'Real_Fed_Funds_Rate', 'Real_Fed_Funds_Rate_12mo_chg',
                'CPI_3mo_pct_chg_annualized', 'CPI_12mo_pct_chg',
                'CPI_3mo_vs_12mo', '10Y_Treasury_Rate_12mo_chg',
                '3M_Treasury_Rate_12mo_chg', '3M_10Y_Treasury_Spread',
                '3M_10Y_Treasury_Spread_12mo_chg',
                '5Y_10Y_Treasury_Spread', 'S&P_500_3mo_chg',
                'S&P_500_12mo_chg', 'S&P_500_3mo_vs_12mo',
                'IPI_3mo_pct_chg_annualized', 'IPI_12mo_pct_chg',
                'IPI_3mo_vs_12mo']
    final_df_output = final_df_output[new_cols]
    print('\t|--Finished creating final dataset!')
    return final_df_output

def save_final_data(final_df_output):    
    print('\t|--Saving dataset {}'.format(path.final_data))
    final_df_output.to_csv(path.final_data,index=False)

    
def save_data(df, file_path):
    print("|--Saving Data {}".format(file_path))
    if CONFIG.save_cloud and CONFIG.save_local:
        save_cloud(df, file_path)
        save_local(df, path.dir_path + file_path)
    elif CONFIG.save_cloud and not CONFIG.save_local:
        save_cloud(df, file_path)
    elif not CONFIG.save_local and  CONFIG.save_local:
        save_local(df, path.dir_path + file_path)
    
# def save_cloud(df, file_path):
#     from google.cloud import storage
#     storage_client = storage.Client.from_service_account_json(
#         path.credentials
#     )
#     bucket = storage_client.get_bucket('recession-predictor')
#     bucket.blob(file_path).upload_from_string(df.to_csv(index=False), 'text/csv')
#     print("\t|--Saved to Cloud")
    
# def save_local(df, file_path):
#     global primary_df_output
#     df.to_csv(file_path,index=False)
#     print("\t|--Saved to local")

# def load_local(file_path):
#     return pd.read_csv(file_path)

# def load_cloud(file_path):
#     from google.cloud import storage
#     import io
#     storage_client = storage.Client.from_service_account_json(
#         path.credentials
#     )
#     bucket = storage_client.get_bucket('recession-predictor')
    
#     blob = bucket.blob(file_path)
#     data = blob.download_as_string()
#     df = pd.read_csv(io.BytesIO(data))
#     return df