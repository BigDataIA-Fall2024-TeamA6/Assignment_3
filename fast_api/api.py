from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import snowflake.connector
import boto3
from io import BytesIO
from PIL import Image
import base64
import bcrypt
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
    image_key: str


# Pydantic model for user creation
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    username: str
    password: str

# Pydantic model for user login
class UserLogin(BaseModel):
    username: str
    password: str

# API to create a new user
@app.post("/create_user/")
async def create_user(user: UserCreate):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Hash the password before storing it in the database
    hashed_password = bcrypt.hashpw(user.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    try:
        # Insert new user into the 'USER_TEST' table
        query = """
        INSERT INTO USER_TEST (FIRSTNAME, LASTNAME, USERNAME, PASSWORD)
        VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (user.first_name, user.last_name, user.username, hashed_password))
        connection.commit()

        return {"message": "User created successfully"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")
    
    finally:
        cursor.close()
        connection.close()


@app.post("/login/")
async def login(user: UserLogin):
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Check if the username exists in the database
        query = "SELECT username, password FROM USER_TEST WHERE username = %s"
        cursor.execute(query, (user.username,))
        result = cursor.fetchone()

        if result:
            db_username, db_password = result
            # Verify the hashed password
            if bcrypt.checkpw(user.password.encode('utf-8'), db_password.encode('utf-8')):
                return {"message": "Login successful", "username": db_username}
            else:
                raise HTTPException(status_code=401, detail="Invalid password")
        else:
            raise HTTPException(status_code=404, detail="Username not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during login: {str(e)}")
    
    finally:
        cursor.close()
        connection.close()


# API to fetch image metadata from Snowflake
@app.get("/image-details/{image_key:path}")
async def get_image_details(image_key: str):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Remove the file extension from image_key to query Snowflake
        base_name = image_key.split('/')[-1].rsplit('.', 1)[0]

        # Query the Snowflake database to retrieve title and brief
        query = "SELECT title, brief FROM test WHERE image_key = %s"
        cursor.execute(query, (base_name,))
        result = cursor.fetchone()

        if result:
            title, brief = result
            return {"title": title, "brief": brief}
        else:
            raise HTTPException(status_code=404, detail="Image details not found")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving image details: {str(e)}")

    finally:
        cursor.close()
        conn.close()

# API to fetch image data from S3 and return as base64
@app.get("/fetch-image/{image_key:path}")
async def fetch_image(image_key: str):
    s3 = get_s3_client()
    try:
        image_object = s3.get_object(Bucket=S3_BUCKET_NAME, Key=image_key)
        image_data = image_object['Body'].read()

        # Convert image data to base64
        img = Image.open(BytesIO(image_data))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

        return {"image_base64": img_base64}
    
    except s3.exceptions.NoSuchKey:
        raise HTTPException(status_code=404, detail=f"Image {image_key} not found in S3.")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching image from S3: {str(e)}")

# API to list all images in S3 bucket
@app.get("/list-images")
async def list_images():
    s3 = get_s3_client()
    try:
        response = s3.list_objects_v2(Bucket=S3_BUCKET_NAME, Prefix="test/")
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
