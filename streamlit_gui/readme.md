
# How to set up a container

First cd into the parent directory where `Dockerfile` is. 

cd ../streamlit_gui


gcloud config set project  [project_id] 

#### Test locally

``` bash
docker build -t recession_model:v1.0  -f  ./streamlit_gui/Dockerfile .   
export MYPORT=9090
docker container kill recessiontest
docker run --rm --name recessiontest -p 8901:${MYPORT} -e PORT=${MYPORT} recession_model:v1.0
```

#### Deploy to google cloud container registry

**Note you must have gcloud SDK installed locally bofore executing next set of commands**
 
``` bash
docker tag recession_model:v1.0 gcr.io/[project_id]/recession_model:v1.0    
```

* push

``` bash
docker push gcr.io/[project_id]/recession_model:v1.0 
```

* deploy


```
gcloud run deploy recession-ui-container --image gcr.io/[project_id]/recession_model:v1.0 --platform managed  --allow-unauthenticated --max-instances=1 --region us-central1 --memory 2Gi --timeout=900
```
    
### Note

Must also filled secrets.py file with the credentials include:
* dir_path =  MAIN_PATH
* api_key = FRED_API_KEY
* service_account_file = NAME_OF_SERVICE_ACCOUNT
* project_id = PROJECT_ID 