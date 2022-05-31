# Set up

There are two files missing from this directory that must be added. 

service_account.json - is the service account to allow the project write to the storage in the cloud regardless where it run from
secrets.py - has infomration on API_KEY, PROJECT_ID etc


### service_account.json

To be able to run this locally you will need to create service account in your project that you will deploy the project to and download the service account key json file. 

### secrets.py

Must also filled secrets.py file with the credentials include:
* dir_path =  MAIN_PATH
* api_key = FRED_API_KEY
* service_account_file = NAME_OF_SERVICE_ACCOUNT
* project_id = PROJECT_ID 

To set up the etl must enable the following API in google cloud:

* eable Cloud function API
* enable Cloud Build API
* enable cloud scheduler API


### cloud scheduler CLI

This function will be deployed as a cloud function. It will be triggered via pub/sub topic. To trigger the function Cloud Scheduler will send a  message to pub/sub topic daily which will trigger the function to get the daily etl started. 

Set up of cloud scheduler:

```
gcloud config set account [email]
gcloud config set project [project_id] 


gcloud functions deploy getdatafunction  --entry-point main --runtime python37 --trigger-resource etl-topic --trigger-event google.pubsub.topic.publish --timeout 540s 
gcloud scheduler jobs create pubsub run_fred_etl --schedule "1 0 * * 1-5 (America/Detroit)" --time-zone "America/New_York"   --topic etl-topic --message-body "Not relevant here"
``` 