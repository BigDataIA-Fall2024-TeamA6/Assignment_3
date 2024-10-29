from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
import boto3
import snowflake.connector
import json
import time
import pandas as pd
import requests
import os
from dotenv import load_dotenv
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def setup_chrome_driver():
    from selenium import webdriver
    """Setup and return Chrome WebDriver"""
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Remote(f'selenium_remote:4444/wd/hub',options=chrome_options)
    return driver

def scrape_pdfs(**context):
    """
    Task to scrape PDF data from the website
    """
    try:
        driver = setup_chrome_driver()
        
        base_url = 'https://rpc.cfainstitute.org/en/research-foundation/publications#'
        url_params = 'sort=%40officialz32xdate%20descending&f:SeriesContent=[Research%20Foundation]'
        image_url = 'https://png.pngtree.com/png-clipart/20220612/original/pngtree-pdf-file-icon-png-png-image_7965915.png'
        
        def get_pdf_title(row):
            try:
                pdf_title = row.find_element(By.CLASS_NAME, 'CoveoResultLink').text
                return pdf_title.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
            except Exception as e:
                logger.error(f"Error retrieving PDF title: {e}")
                return None
            
        def get_webpage_link(row):
            try:
                result_link = row.find_element(By.CLASS_NAME, 'CoveoResultLink').get_attribute('href')
                return result_link
            except Exception as e:
                logger.error(f"Error getting webpage link {e}")
                return ""
        
        def get_image_link(row):
            try:
                image_link = row.find_element(By.CLASS_NAME,'coveo-result-image').get_attribute('src')
                image_link = image_link.split("?")[0]
                return image_link
            except Exception as e:
                logger.error(f"Error getting image link {e}")
                return image_url

        def get_pdf_documents(data):
            try:
                for pdf_info in data:
                    driver.get(pdf_info['webpage_link'])
                    time.sleep(3)
                    pdf_info['pdf_link'] = driver.find_element(By.CSS_SELECTOR, 'a[href$=".pdf"]').get_attribute('href')
                    logger.info(f"Document {pdf_info['pdf_link']} extracted")
                return data
            except Exception as e:
                logger.error(f"Error extracting PDF document links: {e}")
                return data
            
        def get_pdf_summary(row):
            try:
                summary_text = row.find_element(By.CLASS_NAME,'result-body').text
                summary_text = summary_text.encode('utf-8').decode('unicode_escape').encode('latin1').decode('utf-8')
                return summary_text
            except Exception as e:
                logger.error(f"Error getting summary text: {e}")
                return ""

        def scrape_single_page(page_url):
            driver.get(page_url)
            time.sleep(7)
            rows = driver.find_elements(By.CSS_SELECTOR, '.coveo-result-frame.coveoforsitecore-template')
            page_data = []
            
            for row_num, row in enumerate(rows):
                try:
                    row_data = {
                        'webpage_link': get_webpage_link(row),
                        'title': get_pdf_title(row),
                        'image_link': get_image_link(row),
                        'summary_text': get_pdf_summary(row)
                    }
                    page_data.append(row_data)
                    logger.info(f"Row {row_num} added")
                except Exception as e:
                    logger.error(f"Error scraping row {row_num}: {e}")
            return page_data

        
        all_data = []
        for page_num in range(0, 10 * 10, 10):
            page_url = f"{base_url}&first={page_num}&{url_params}"
            page_data = scrape_single_page(page_url)
            all_data.extend(page_data)
            logger.info(f"Page {page_num} updated")
            time.sleep(2)

        # Get PDF documents
        pdf_data = get_pdf_documents(all_data)
        
        # Save to JSON file
        output_path = "/tmp/scraped_data.json"
        with open(output_path, 'w') as file:
            json.dump(pdf_data, file, indent=4)
            
        # Push the file path to XCom
        context['task_instance'].xcom_push(key='json_file_path', value=output_path)
        logger.info("Successfully completed PDF scraping")
        
        driver.quit()
        
    except Exception as e:
        logger.error(f"Error in PDF scraping task: {str(e)}")
        raise

def upload_to_snowflake_and_s3(**context):
    """
    Task to upload scraped data to Snowflake and S3
    """
    try:
        # Get JSON file path from previous task
        json_file_path = context['task_instance'].xcom_pull(
            task_ids='scrape_pdfs_task',
            key='json_file_path'
        )
        
        # S3 Configuration
        s3_client = boto3.client(
            's3',
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name='us-east-1'
        )
        
        # Snowflake Configuration
        conn = snowflake.connector.connect(
            user=os.getenv("SNOWFLAKE_USER"),
            password=os.getenv("SNOWFLAKE_PASSWORD"),
            account=os.getenv("SNOWFLAKE_ACCOUNT"),
            warehouse=os.getenv("SNOWFLAKE_WAREHOUSE"),
            database=os.getenv("SNOWFLAKE_DATABASE"),
            schema=os.getenv("SNOWFLAKE_SCHEMA")
        )
        
        cursor = conn.cursor()
        
        def upload_to_s3(file_url, s3_bucket, s3_key):
            try:
                response = requests.get(file_url, stream=True)
                if response.status_code == 200:
                    s3_client.upload_fileobj(
                        response.raw, #PDF Filename
                        s3_bucket, #S3 Bucket name
                        f"Research-Foundation/{s3_key}" #PDFname to be saved in S3
                    )
                logger.info(f"Successfully uploaded {s3_key} to {s3_bucket}")
                    
                s3_link = f"https://bdia-assignment-3.s3.us-east-1.amazonaws.com/{s3_bucket}/{s3_key}"
                return s3_link
            except Exception as e:
                logger.error(f"Failed to upload {s3_key} to S3: {str(e)}")
                raise
        
        # Load JSON data
        with open(json_file_path, 'r') as file:
            pdf_data = pd.DataFrame(json.load(file))
        
        # Upload files to S3 and Snowflake
        insert_query = """
            INSERT INTO research_foundation 
            (pdf_key, title, image_link, pdf_link, pdf_summary) 
            VALUES (%s, %s, %s, %s, %s)
        """
        
        for _, row in pdf_data.iterrows():
            pdf_name = row['pdf_link'].split("/")[-1] # pdf_doc.pdf
            image_name = ''.join([pdf_name.split(".")[0], ".", row['image_link'].split("/")[-1].split(".")[-1]]) # filename(w/o .pdf),dot,file_ext
            
            pdf_s3link = upload_to_s3(row['pdf_link'], "bdia-assignment-3", pdf_name)
            image_s3link = upload_to_s3(row['image_link'], "bdia-assignment-3", image_name)
            
            cursor.execute(insert_query, (
                row['pdf_link'].split('/')[-1],
                row['title'],
                image_s3link,
                pdf_s3link,
                row['summary_text']
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("Successfully uploaded data to S3 and Snowflake")
        
    except Exception as e:
        logger.error(f"Error in upload task: {str(e)}")
        raise


# Create the DAG
default_args = {
    'owner': 'user',
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2024, 10, 1),
    'execution_timeout': timedelta(minutes=15)
}


dag =  DAG(
    'research_foundation_pipeline',
    default_args= default_args,
    description='Pipeline to scrape Research Foundation PDFs and upload to Snowflake and S3',
    schedule_interval=None, 
    catchup=False
)
    
    # Task 1: Scrape PDFs
scrape_pdfs_task = PythonOperator(
    task_id='scrape_pdfs_task',
    python_callable=scrape_pdfs,
    provide_context=True,
    execution_timeout= timedelta(minutes=15),    
    dag = dag
)
    
    # Task 2: Upload to Snowflake and S3
upload_task = PythonOperator(
    task_id='upload_to_snowflake_and_s3_task',
    python_callable=upload_to_snowflake_and_s3,
    provide_context=True,
    execution_timeout= timedelta(minutes=15),    
    dag = dag
)

    # Set task dependencies
scrape_pdfs_task >> upload_task