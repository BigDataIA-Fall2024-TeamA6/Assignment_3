import os
import json
import boto3
import requests
import pandas as pd
from dotenv import load_dotenv
import snowflake.connector

load_dotenv()

json_file_path = r'C:\Users\visho\Documents\BDIAProjects\Assignment_3\scraped_data.json'
AWS_LINK = 'https://bdia-assignment-3.s3.us-east-1.amazonaws.com'
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")
S3_BUCKET_NAME = "bdia-assignment-3"
S3_FOLDER_NAME = 'Research-Foundation'

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name='us-east-1'
)

conn = snowflake.connector.connect(
    user=SNOWFLAKE_USER,
    password=SNOWFLAKE_PASSWORD,
    account=SNOWFLAKE_ACCOUNT,
    warehouse=SNOWFLAKE_WAREHOUSE,
    database=SNOWFLAKE_DATABASE,
    schema=SNOWFLAKE_SCHEMA
)

cursor = conn.cursor()


#Load the JSON data from the JSON file
def load_json(json_fp):
    try:
        with open(json_fp) as file:
            json_data_df = pd.DataFrame(json.load(file))
        return json_data_df
    except Exception as e:
        print(f"Error loading JSON file {e}")
        return


def upload_files(pdf_data):
    try:
        insert_query = "INSERT INTO research_foundation (pdf_key,title, image_link, pdf_link,pdf_summary) VALUES (%s, %s, %s, %s,%s)"
        for _,row in pdf_data.iterrows():
            pdf_name = row['pdf_link'].split("/")[-1]
            image_name = ''.join([pdf_name.split(".")[0],".", row['image_link'].split("/")[-1].split(".")[-1]])
            pdf_s3link = upload_to_s3(row['pdf_link'],S3_BUCKET_NAME,pdf_name)
            image_s3link = upload_to_s3(row['image_link'],S3_BUCKET_NAME,image_name)
            
            title = row.get('title')
            pdf_key = row.get('webpage_link').split('/')[-1]
            image_link = image_s3link
            pdf_link = pdf_s3link
            pdf_summary = row.get('summary_text')

            cursor.execute(insert_query, (pdf_key,title, image_link, pdf_link, pdf_summary))
        conn.commit()
        cursor.close()
        conn.close()
        print("Uploaded to S3 and Snowflake")  
        return
    except Exception as e:
        print(f"Please check JSON file. Error s: {e}")
        
        
def upload_to_s3(file_url, s3_bucket, s3_key):
    """Upload file content to S3."""
    try:
        response = requests.get(file_url,stream=True)
        if response.status_code == 200:
            s3_client.upload_fileobj(response.raw, s3_bucket, S3_FOLDER_NAME + "/" + s3_key)        
        # print(f"Successfully uploaded {s3_key} to s3://{s3_bucket}/{s3_key}")
        s3_link = ''.join([AWS_LINK,"/",S3_BUCKET_NAME,"/",s3_key])
        return s3_link
    except Exception as e:
        print(f"Failed to upload {s3_key} to S3: {str(e)}")
        
        
pdf_data = load_json(json_file_path)
upload_files(pdf_data)


            
