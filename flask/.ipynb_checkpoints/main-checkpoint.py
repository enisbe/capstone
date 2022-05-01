from flask import Flask, request, jsonify, render_template
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
# from joblib import dump, load
import logging
from flask.logging import create_logger

import pickle

import pandas as pd
import json 

app = Flask(__name__)
LOG = create_logger(app)
LOG.setLevel(logging.INFO)


@app.route('/predict24',methods=['POST'])
def predict():
    """ Predict route. Only Handles POST requests"""
    


    json_payload =   request.json
    # return json_payload
    LOG.info(print(type(json_payload)))
    LOG.info("JSON payload: sucess ")

    X_score = pd.DataFrame(json_payload)
    # scaler.transform(X_score)
  
    needed =['Dates', 'Payrolls_3mo_vs_12mo', 'Real_Fed_Funds_Rate_12mo_chg',
       'CPI_3mo_pct_chg_annualized', '10Y_Treasury_Rate_12mo_chg',
       '3M_10Y_Treasury_Spread', 'S&P_500_12mo_chg']
    if len(set(needed) - set(X_score.columns)) > 0:
        return {
            "response": "failure",
            "message": "Mssing Columns."
        }

    models = [6,12,24]
    
    model_response = {}
    for model in models:
        mod = pickle.load(open(f'./model/model{str(model)}.pickle', "rb"))
        scaler = pickle.load(open(f'./model/scaler{str(model)}.pickle', "rb")) 
        LOG.info(X_score.shape) 
        predicted = mod.predict_proba(scaler.transform(X_score.drop("Dates",axis=1)))[:,1]
        prediction = X_score.copy()
        prediction['prediction'] =predicted
        model_response[f"{str(model)}mo"] = prediction[['Dates','prediction']].to_dict()
        LOG.info("Prediction: sucess ")
    return  json.dumps(model_response) # X_score[['Dates','prediction']].to_dict()
    return jsonify({'predicted=1': list(predicted)})

if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='0.0.0.0', port=8080, debug=True)