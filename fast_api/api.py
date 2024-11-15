from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import snowflake.connector
import boto3
from io import BytesIO
from PIL import Image
import base64
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# FastAPI instance
app = FastAPI()

# AWS and Snowflake credentials from environment variables
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")

SNOWFLAKE_USER = os.getenv("SNOWFLAKE_USER")
SNOWFLAKE_PASSWORD = os.getenv("SNOWFLAKE_PASSWORD")
SNOWFLAKE_ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
SNOWFLAKE_WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")
SNOWFLAKE_DATABASE = os.getenv("SNOWFLAKE_DATABASE")
SNOWFLAKE_SCHEMA = os.getenv("SNOWFLAKE_SCHEMA")

# Helper function to connect to S3
def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

# Helper function to connect to Snowflake
def get_db_connection():
    connection = snowflake.connector.connect(
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        account=SNOWFLAKE_ACCOUNT,
        warehouse=SNOWFLAKE_WAREHOUSE,
        database=SNOWFLAKE_DATABASE,
        schema=SNOWFLAKE_SCHEMA
    )
    return connection

# Pydantic model for Image Metadata
class ImageMetadata(BaseModel):
    title: str
    brief: str
    pdf_key: str


# API to fetch image metadata from Snowflake
S3_BASE_URL = "https://bdia-assignment-3.s3.us-east-1.amazonaws.com/"

@app.get("/image-details/{pdf_key:path}")
async def get_image_details(pdf_key: str):
    try:
        # Establish a database connection
        conn = get_db_connection()
        cursor = conn.cursor()

        # Construct the full image link URL
        full_image_link = f"{S3_BASE_URL}{pdf_key}"

        # Query the Snowflake database to retrieve title and pdf_summary where image_link matches
        query = "SELECT title, pdf_summary, pdf_key FROM research_foundation WHERE image_link = %s"
        cursor.execute(query, (full_image_link,))
        result = cursor.fetchone()

        if result:
            title, brief, pdf_key_value = result
            return {"title": title, "pdf_summary": brief, "pdf_key": pdf_key_value}
        else:
            #logger.warning(f"No details found for image link: {full_image_link}")
            raise HTTPException(status_code=404, detail="Image details not found")

    except Exception as e:
        #logger.error("Error retrieving image details", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error retrieving image details: {str(e)}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# API to fetch image data from S3 and return as base64
@app.get("/fetch-image/{pdf_key:path}")
async def fetch_image(pdf_key: str):
    s3 = get_s3_client()
    try:
        print(pdf_key)
        image_object = s3.get_object(Bucket=S3_BUCKET_NAME, Key=pdf_key)
        image_data = image_object['Body'].read()

        # Open the image and check its format
        img = Image.open(BytesIO(image_data))
        img_format = img.format  # Original format (e.g., PNG, JPEG)

        # Convert CMYK images to RGB to ensure compatibility with PNG or JPEG
        if img.mode == "CMYK":
            img = img.convert("RGB")

        # Prepare buffer for image data
        buffered = BytesIO()
        img.save(buffered, format=img_format if img_format in ["PNG", "JPEG"] else "PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return {"image_base64": img_base64, "format": img_format}

    except s3.exceptions.NoSuchKey:
        # Load a placeholder image if the original is not found
        placeholder_key = "Research-Foundation/image-not-available.png"
        image_object = s3.get_object(Bucket=S3_BUCKET_NAME, Key=placeholder_key)
        image_data = image_object['Body'].read()

        # Open and process the placeholder image
        img = Image.open(BytesIO(image_data))
        if img.mode == "CMYK":
            img = img.convert("RGB")

        img_format = img.format
        buffered = BytesIO()
        img.save(buffered, format=img_format if img_format in ["PNG", "JPEG"] else "PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return {"image_base64": img_base64, "format": img_format}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching image from S3: {str(e)}")

# API to list all images in S3 bucket
@app.get("/list-images")
async def list_images():
    s3 = get_s3_client()
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix="Research-Foundation/")
        if 'Contents' not in response:
            raise HTTPException(status_code=404, detail="No images found in S3 bucket")

        image_files = [item['Key'] for item in response['Contents'] if item['Key'].endswith(('.png', '.jpg', '.jpeg'))]
        return image_files
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing images: {str(e)}")

# Run the API server using: uvicorn api:app --reload
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
