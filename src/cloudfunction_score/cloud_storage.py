import config as config
import path as path
import os
import pandas as pd
import secrets
 
def save_data(df, file_path):
    if config.save_cloud and config.save_local:
        print("|--Saving Data Locally and in Cloud {}".format(file_path))
        save_cloud(df, file_path)
        save_local(df, path.dir_path + file_path)
    elif config.save_cloud and not config.save_local:
        print("|--Saving Cloud Only{}".format(file_path))
        save_cloud(df, file_path)
    elif not config.save_cloud and  config.save_local:
        print("|--Saving Locally Only {}".format(path.dir_path + file_path))
        save_local(df, path.dir_path + file_path)
        
        

def save_cloud(df, file_path, bucket_name=secrets.project_id):
    from google.cloud import storage
    storage_client = storage.Client.from_service_account_json(
        path.credentials
    )
    bucket = storage_client.get_bucket(bucket_name)
    bucket.blob(file_path).upload_from_string(df.to_csv(index=False), 'text/csv')
    print("\t|--Saved to Cloud")

    
    
def save_local(df, file_path): 
    df.to_csv(file_path,index=False)
    print("\t|--Saved to local")

    

def load_local(file_path):
    return pd.read_csv(file_path)



def load_cloud(file_path, bucket_name=secrets.project_id):
    from google.cloud import storage
    import io
    storage_client = storage.Client.from_service_account_json(
        path.credentials
    )
    bucket = storage_client.get_bucket(bucket_name)
    
    blob = bucket.blob(file_path)
    data = blob.download_as_string()
    df = pd.read_csv(io.BytesIO(data))
    return df



def load_data(file_path):    
 
    if config.read_cloud:
        print(f"\t|--Read Cloud {file_path}")
        df = load_cloud(file_path)
    else:
        print(f"\t|--Read Local {file_path}")
        df = load_local(path.dir_path + file_path)
    return df
