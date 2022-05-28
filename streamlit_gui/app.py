import pandas as pd
import streamlit as st
import datetime as dt
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import recession_graph as plt
import sys
from google.cloud import storage as cs_storage
import pytz
tz = pytz.timezone("US/Eastern")
                   
                   

if "../" not in sys.path:
    sys.path.insert(0,"../")

if "./common" not in sys.path:
    sys.path.insert(0,"./common")
    
import common.config as config
import common.cloud_storage as storage
import common.path as path
import forecast
import common.secrets as secrets


storage_client = cs_storage.Client.from_service_account_json(
    path.credentials
)
bucket = storage_client.bucket(secrets.project_id)
blob = bucket.get_blob(path.prediction_data)
last_update = blob.updated.replace(tzinfo=pytz.utc).astimezone(tz)




import importlib as imp
imp.reload(storage.config)
imp.reload(path)


 
st.set_page_config(
    page_title="Probability of Recession Model",
    layout="wide")
 
    
st.header("Recession Model")
st.write("Latest Update: " + last_update.strftime("%Y-%m-%d"))

st.markdown("""
-----
This is a probability of recession model developed using SVM method. The model predicts the probability of a recession occurring over the next 24 months.
Recession predictors used: 
* `Payrolls_3mo_vs_12mo` - The difference between 3 months payroll change (annualized) and 12 months payroll change
* `Real_Fed_Funds_Rate_12mo_chg` - Real Fed Fund Rates difference compared to 12 months
* `CPI_3mo_pct_chg_annualized` - CPI 3 months percentage change annualized
* `10Y_Treasury_Rate_12mo_chg` - 12 month rate difference in 10 Year Treasury bond
* `CPI_3mo_pct_chg_annualized` - Inflation -> CPI 3 months percentage change annualized
* `3M_10Y_Treasury_Spread` - Spread between 10 year treasury 3 months tresury rates (Measure of inverted yield curve)
* `S&P_500_12mo_chg` - S&P500 annual percentage return

**Instruction to use forecast:**

You can provide your CSV file with forecasted raw variables (e.g. SP500 index) and observe how the probability of recession changes as result.

The provided file must contain the following columns:
`Dates,Non-farm_Payrolls,Civilian_Unemployment_Rate,Effective_Fed_Funds,CPI_All_Items,10Y_Treasury_Rate,3_Month_T-Bill_Rate,S&P_500_Index`


-----
""")


df_final =storage.load_data(path.final_data)
df_pred = storage.load_data(path.prediction_data)
df_raw = storage.load_data(path.latest_data)


year = st.sidebar.selectbox(
    'View after year:',
     list(range(1976,2022))

)

raw = st.sidebar.checkbox('Raw Predictors')
smoothed = st.sidebar.checkbox('Smoothed Probability')
uploaded_file =   st.sidebar.file_uploader("Upload Forecast")

forecast_begin = None


if uploaded_file is not None:
    forecast_df = pd.read_csv(uploaded_file)  
    # df_pred = prediction(forecast_df)
    
    df_pred, df_final, df_raw, forecast_begin  = forecast.prediction(forecast_df,df_raw, df_final, df_pred)
# prediction(forecast_df, df_raw,  full_df, old_prediction)

# Filter for dates
df_final = df_final[pd.to_datetime(df_final['Dates']).dt.year>=int(year)]
df_pred = df_pred[pd.to_datetime(df_pred['Dates']).dt.year>=int(year)]
df_raw = df_raw[pd.to_datetime(df_raw['Dates']).dt.year>=int(year)]


    
st.markdown("""
            **Probability of recession relative to 3 months ago**
             
            """)

# war = st.text('Probability of recession relative to 3 quarter ago')

df_pred['Pred_Recession_within_24mo_smoothed'] = df_pred['Pred_Recession_within_24mo'].ewm(halflife=3, adjust=True).mean()

if smoothed:
    df_pred['Pred_Recession_within_24mo_3mo_change'] = df_pred ['Pred_Recession_within_24mo_smoothed'].diff(3)

else:
    df_pred['Pred_Recession_within_24mo_3mo_change'] = df_pred ['Pred_Recession_within_24mo'].diff(3)



col_num = 6
cols = st.columns(col_num)

if smoothed:
    for i, row in enumerate(df_pred[['Dates','Pred_Recession_within_24mo_smoothed', 'Pred_Recession_within_24mo_3mo_change']].tail(col_num).iterrows()):
        r = row[1]   
        cols[i].metric(f"{r['Dates']}", f"{r['Pred_Recession_within_24mo_smoothed']:.1%}", f"{ r['Pred_Recession_within_24mo_3mo_change']:.2%}" , delta_color='inverse')


else:
    for i, row in enumerate(df_pred[['Dates','Pred_Recession_within_24mo', 'Pred_Recession_within_24mo_3mo_change']].tail(col_num).iterrows()):
        r = row[1]   
        cols[i].metric(f"{r['Dates']}", f"{r['Pred_Recession_within_24mo']:.1%}", f"{ r['Pred_Recession_within_24mo_3mo_change']:.2%}" , delta_color='inverse')



feature_names = ['Payrolls_3mo_vs_12mo',
                      'Real_Fed_Funds_Rate_12mo_chg',
                      'CPI_3mo_pct_chg_annualized',
                      '10Y_Treasury_Rate_12mo_chg',
                      '3M_10Y_Treasury_Spread',
                      'S&P_500_12mo_chg']

raw_vars = ['Non-farm_Payrolls','Effective_Fed_Funds','CPI_All_Items','10Y_Treasury_Rate','3_Month_T-Bill_Rate','S&P_500_Index']


if smoothed:
    fig = plt.recession_figure(df_pred[["Dates", 'Pred_Recession_within_24mo_smoothed']], title="Probabability of Recessing 24mo Smoothed", forecast_begin=forecast_begin)
else:
    fig = plt.recession_figure(df_pred[["Dates", 'Pred_Recession_within_24mo']], title="Probabability of Recessing 24mo", forecast_begin=forecast_begin)
 

config={
        'modeBarButtonsToAdd': ['drawline']
    }



st.plotly_chart(fig, use_container_width=True, config=config)


if raw:
    for feature in raw_vars:
        fig = plt.recession_figure(df_raw[["Dates", feature]], forecast_begin=forecast_begin)
        st.plotly_chart(fig, use_container_width=True, config=config)

else:

    for feature in feature_names:
        fig = plt.recession_figure(df_final[["Dates", feature]], forecast_begin=forecast_begin)
        st.plotly_chart(fig, use_container_width=True, config=config)
