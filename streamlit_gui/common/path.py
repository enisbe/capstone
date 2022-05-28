
import os
import datetime as dt
import os
import common.secrets as secrets

dir_path = secrets.dir_path  

api_key = secrets.api_key  

# os.getcwd() # get you directory of the file loading the module
# __file__ # get full directory of the module file

cwd = os.path.dirname(__file__) + "/"

credentials =  cwd +  secrets.service_account_file
 
 

sp500_precutoff_data = ( "data/auxiliary/sp500_fix.csv")
latest_data = ( "data/raw/latest_data.csv")
latest_data_stale = ( "data/raw/latest_data_stale.csv")

latest_secondary_data = ( "data/processed_data/latest_secondary_data.csv")
final_data  = ( "data/processed_data/final_data.csv")
prediction_data = ( "data/prediction/test_prediction.csv")

  