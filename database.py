import os
from azure.storage.blob import BlobServiceClient


def uploadToBlobStorage(file_name):
    connect_str = xxx
    container_name = "otomoto"
    
    blob_service_client = BlobServiceClient.from_connection_string(connect_str)
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=file_name)
    
    with open(file_name, "rb") as data:
        blob_client.upload_blob(data)
        print(f"Uploaded {file_name}.")
        
        
if __name__ == "__main__":
   uploadToBlobStorage("otomoto_2023-08-07.csv")