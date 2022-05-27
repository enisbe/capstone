from score import score
import path as path


def main(event, context):
    """Triggered by a change to a Cloud Storage bucket.
    Args:
         event (dict): Event payload.
         context (google.cloud.functions.Context): Metadata for the event.
    """
    file = event
 
    if file['name']== path.final_data:
        print(f"Trigger file found: {file['name']}.")

        print("|--Execution score")
        score()
    else:
        print(f"File: {file['name']}.")

 