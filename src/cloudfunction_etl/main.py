import importlib as imp
import get_primary_data as get_data
import process_secondary_data as secondary_data
import importlib as imp
from string import Template
import datetime
import config as config
import cloud_storage as storage
import path as path



def process_data(data, context):
    """
    Process Primary
    """
    current_time = datetime.datetime.utcnow()
    log_message = Template('Function Started  on $time')
    print(log_message.safe_substitute(time=current_time))
          
    get_data.get_fred_data()
    get_data.get_yahoo_data()
    get_data.fix_s500()
    get_data.find_shortest_series()
    get_data.combine_data()
    get_data.update_data()
    storage.save_data(df = get_data.primary_df_output,   file_path = path.latest_data)
    storage.save_data(df = get_data.primary_df_output_stale,   file_path = path.latest_data_stale)
    
    """
    Process Secondary and Final data
    """
    # Load Primary Data
    if config.read_cloud:
        primary_df_output = storage.load_cloud(path.latest_data)
    else:
        primary_df_output = storage.load_local(path.dir_path + path.latest_data)

    # Process Secondary Data and Save    
    secondary_df_output = secondary_data.create_secondary_data(primary_df_output) 
    storage.save_data(df = secondary_df_output,   file_path = path.latest_secondary_data)

    # Load Saved secondary and enhance (final_data)
    if config.read_cloud:
        latest_secondary_data = storage.load_cloud(path.latest_secondary_data)
    else:
        latest_secondary_data = storage.load_local(path.dir_path + path.latest_secondary_data)

    final_data = secondary_data.create_final_data(latest_secondary_data)

    storage.save_data(df = final_data,   file_path = path.final_data)
          
    current_time = datetime.datetime.utcnow()
    log_message = Template('Function finished  on $time')
    print(log_message.safe_substitute(time=current_time))

# if __name__ == '__main__':
process_data('data', 'context')