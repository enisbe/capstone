# Set up

To set up the etl must enable the following API in google cloud:

* eable Cloud function API
* enable Cloud Build API
* enable cloud scheduler API

To be able to run this locally you will need to create service account in your project that you deploy this to and downlaod service account key json file. 

Must also filled secrets.py file with the credentials include:
* dir_path =  MAIN_PATH
* api_key = FRED_API_KEY
* service_account_file = NAME_OF_SERVICE_ACCOUNT
* project_id = PROJECT_ID 


This function will be deployed as a cloud function. It will be triggered via pub/sub topic. Cloud Scheduler will deploy a message to pub/sub topic daily which will trigger the function to get the daily etl started.

gcloud config set account [email]
gcloud config set project [project_id] 


gcloud functions deploy getdatafunction  --entry-point main --runtime python37 --trigger-resource etl-topic --trigger-event google.pubsub.topic.publish --timeout 540s 
gcloud scheduler jobs create pubsub run_fred_etl --schedule "1 0 * * 1-5 (America/Detroit)" --time-zone "America/New_York"   --topic etl-topic --message-body "Not relevant here"
 