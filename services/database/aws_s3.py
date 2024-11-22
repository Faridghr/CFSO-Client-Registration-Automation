import boto3
from config import Config

class AWSService:
    """
    Handles interactions with AWS services, primarily S3.

    Methods:
        upload_to_s3(file_path, key): Uploads a file to the specified S3 bucket.
        download_file(s3_url): Downloads a file from S3 given its URL.
        upload_file_object(buffer, key, content_type): Uploads a file object to S3.
        generate_presigned_url(key, filename): Generates a pre-signed URL for downloading an object.
    """
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=Config.AWS_ACCESS_KEY,
            aws_secret_access_key=Config.AWS_SECRET_KEY,
            region_name='us-east-1'
        )

    def upload_to_s3(self, file_path, key):
        """
        Uploads a file to S3.

        Args:
            file_path (str): Local path of the file to upload.
            key (str): S3 key (path) for the uploaded file.

        Returns:
            None
        """
        self.s3_client.upload_file(file_path, Config.S3_BUCKET_NAME, key)


    def download_file(self, s3_url):
        """
        Downloads a file from S3.

        Args:
            s3_url (str): URL of the file in S3.

        Returns:
            bytes: The file content as bytes.
        """
        s3_bucket = s3_url.split('/')[2]
        file_key = '/'.join(s3_url.split('/')[3:])
        response = self.s3_client.get_object(Bucket=s3_bucket, Key=file_key)
        return response['Body'].read()
    

    def upload_file_object(self, buffer, key, content_type):
        self.s3_client.upload_fileobj(buffer, self.bucket_name, key, ExtraArgs={'ContentType': content_type})


    def generate_presigned_url(self, key, filename, expiration=3600):
        return self.s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': Config.S3_BUCKET_NAME,
                'Key': key,
                'ResponseContentDisposition': f'attachment; filename="{filename}"'
            },
            ExpiresIn=expiration
        )