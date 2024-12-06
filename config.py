import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

class Config:
    INTERAC_EMAIL = os.getenv('INTERAC_EMAIL')
    X_Api_Key = os.getenv('X-Api-Key')
    JOTFORM_API_KEY = os.getenv('JOTFORM_API_KEY')
    MONGO_USERNAME = os.getenv('MONGO_USERNAME')
    MONGO_PASSWORD = os.getenv('MONGO_PASSWORD')
    MONGO_CLUSTER = os.getenv('MONGO_CLUSTER')
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME')
    S3_FILE_KEY = os.getenv('S3_FILE_KEY')
    SPONSOR_EMAIL_APP_PASSWORD = os.getenv('SPONSOR_EMAIL_APP_PASSWORD')
    SPONSOR_EMAIL_USER = os.getenv('SPONSOR_EMAIL_USER')
    ERROR_NOTIFICATION_EMAIL_RECIEVER = os.getenv('ERROR_NOTIFICATION_EMAIL_RECIEVER')
    CONFIRMATION_SENDER_EMAIL = os.getenv('CONFIRMATION_SENDER_EMAIL')
    CONFIRMATION_SENDER_EMAIL_APP_PASSWORD = os.getenv('CONFIRMATION_SENDER_EMAIL_APP_PASSWORD')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_API_MODEL = os.getenv('OPENAI_API_MODEL')

# from config import Config
