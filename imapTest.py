import boto3
import pandas as pd
from io import StringIO
import yaml
from imap_tools import MailBox, AND, NOT
import logging
from datetime import datetime, timedelta
import re
from thefuzz import fuzz
from thefuzz import process


log_filename = "Validator.log"
logging.basicConfig(
    filename=log_filename,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def load_email_credentials(filepath):
    """
    Loads email credentials from a YAML file.

    Args:
        filepath (str): The path to the YAML file containing the user credentials.

    Returns:
        tuple: A tuple containing the user email (str) and password (str).

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If user or password is missing from the file.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    try:
        with open(filepath, 'r') as file:
            content = file.read()
            credentials = yaml.load(content, Loader=yaml.FullLoader)
            user = credentials.get('user')
            password = credentials.get('password')
            bank_email = credentials.get('bank_email')

            if not user or not password:
                logging.error("User or password missing in the provided YAML file.")
                raise ValueError("Credentials not found or incomplete in yaml file.")
            logging.info("Credentials loaded successfully.")
            return user, password, bank_email
    except FileNotFoundError:
        logging.error("The specified YAML file was not found: {}".format(filepath))
        raise
    except yaml.YAMLError as e:
        logging.error("Error parsing YAML file: {}".format(e))
        raise


def load_s3_config(filepath):
    """
    Loads S3 configuration credentials from a YAML file.

    Args:
        filepath (str): The path to the YAML file containing the S3 configuration.

    Returns:
        tuple: A tuple containing the access_key (str), secret_key (str), and bucket_name (str).

    Raises:
        FileNotFoundError: If the specified file does not exist.
        ValueError: If access_key, secret_key, or bucket_name is missing from the file.
        yaml.YAMLError: If there is an error parsing the YAML file.
    """
    try:
        with open(filepath, 'r') as file:
            content = yaml.load(file, Loader=yaml.FullLoader)
            access_key = content.get('access_key')
            secret_key = content.get('secret_key')
            bucket_name = content.get('bucket_name')
            file_key = content.get('file_key')

            if not access_key or not secret_key or not bucket_name:
                logging.error("Missing required S3 configuration in the YAML file.")
                raise ValueError("S3 configuration is incomplete in YAML file.")
            
            logging.info("S3 configuration loaded successfully.")
            return access_key, secret_key, bucket_name , file_key
    except FileNotFoundError:
        logging.error(f"The specified YAML file was not found: {filepath}")
        raise
    except yaml.YAMLError as e:
        logging.error(f"Error parsing YAML file: {e}")
        raise




def test_match(data):
    """
    Extracts sender, amount, and reference number from email text data.

    Args:
        data (str): The email text from which information is extracted.

    Returns:
        tuple: A tuple containing sender name (str), amount (str), and reference number (str).
               If any information is not found, the respective value will be None.
    """
    sent_from = re.search(r"Sent From:\s*(.*)", data, re.MULTILINE)
    sent_from = sent_from.group(1).strip() if sent_from else None

    amount = re.search(r"Amount: (\$[\d,]+\.\d{2})", data)
    amount = amount.group(1) if amount else None

    reference_number = re.search(r"Reference Number: (\w+)", data)
    reference_number = reference_number.group(1) if reference_number else None
    
    return sent_from, amount, reference_number

def clean_amount(text):
    text = text.replace("$",'')
    text = text.replace(",",'')
    if '.' in text:
        text = text.split('.')[0]
    return text




def email(days):
    """
    Args:
        1. A list of payer First, Middle and Last name.
        2. A list of words likely to contain a reference number.
        3. The amount the customer is expected to pay.
        4. How long should the code check the mailbox(Default 14 days).

    Returns:
        1. A JSON file containing success and error fields, e.g., { 'success': False, 'error': 'description of the error }.

    Main function to process emails:
    - Loads credentials
    - Logs in to the email server
    - Checks email for the past 2 weeks
    - Fetches recent emails from a specific sender
    - Extracts relevant information from each email
    - Logs the extracted information

    Logs errors if any issues occur during the execution.
    """
    try:
        email_user, email_password, sender_email = load_email_credentials("./cred.yaml")
        with MailBox('imap.gmail.com').login(email_user, email_password) as mailbox:
            logging.info("Successfully logged in to the mailbox.")
            last_week_date = (datetime.now() - timedelta(days=days)).date()
            messages = mailbox.fetch(AND(from_=sender_email, date_gte=last_week_date))

            result = []
            for msg in messages:
                sent_from, amount, reference_number = test_match(msg.text)
                amount = clean_amount(amount)
                date = msg.date_str
                result.append({"Reference" : reference_number , "Sent_From":sent_from, "Date":date, "Amount":amount, "Used":False})
                logging.info(f"Processed email from {sent_from} with amount {amount} and reference number {reference_number}")

            return result
        
    except Exception as e:
        logging.error("An error occurred: {}".format(e))



def check_reference_in_csv(reference_number, df ):
    """
    Checks if a reference number exists in the provided DataFrame.
    """
    exists = reference_number in df['Reference'].values
    logging.info(f"Checked reference number {reference_number}: {'Found' if exists else 'Not Found'}")
    return exists


def add_unique_rows_to_csv(new_data_list,s3, bucket_name , file_key):
    """
    Adds only unique rows to an existing CSV file in S3 based on ReferenceNumber.
    """
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        csv_content = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_content))
        logging.info("CSV file loaded from S3 successfully.")
    except s3.exceptions.NoSuchKey:
        logging.warning("CSV file not found in S3.")
        return "CSV file not found in S3."

    unique_rows = []
    for data in new_data_list:
        if not check_reference_in_csv(data["Reference"], df):
            unique_rows.append(data)
            logging.info(f"Adding new row for reference number {data['Reference']}.")
        else:
            logging.info(f"Reference number {data['Reference']} already exists. Skipping addition.")

    if unique_rows:
        df = pd.concat([df, pd.DataFrame(unique_rows)], ignore_index=True)
        csv_buffer = StringIO()
        df.to_csv(csv_buffer, index=False)
        s3.put_object(Bucket=bucket_name, Key=file_key, Body=csv_buffer.getvalue())
        logging.info("Unique rows added to CSV file in S3.")
    else:
        logging.info("No new unique rows to add.")


def validate_reference_by_name(name, amount, s3, bucket_name, file_key):
    """
    Function to validate if the given name matches a record in the CSV file stored in S3
    among rows where 'Used' is not True. If a match is found, it validates the amount and
    updates the 'Used' column to True.
    
    Args:
        name (str): The name to search for in the 'Sent_From' column.
        amount (float): The amount to validate.
        s3 (boto3.client): The S3 client.
        bucket_name (str): The S3 bucket name.
        file_key (str): The file key of the CSV in the bucket.

    Returns:
        dict: A status and message indicating the result.
    """
    try:
        response = s3.get_object(Bucket=bucket_name, Key=file_key)
        csv_content = response['Body'].read().decode('utf-8')
        df = pd.read_csv(StringIO(csv_content))
        logging.info("CSV file loaded from S3 successfully for validation.")
    except s3.exceptions.NoSuchKey:
        logging.error("CSV file not found in S3.")
        return {'status': False, "message": "CSV file not found in S3."}


    df_unused = df[df['Used'] != True]
    if df_unused.empty:
        logging.warning("No unused records found in the CSV.")
        return {'status': False, "message": "No unused records found."}


    best_match = process.extractOne(name, df_unused['Sent_From'], scorer=fuzz.token_set_ratio)
    print(best_match)
    amount = clean_amount(amount)
    if best_match and best_match[1] >= 95:  # Threshold for a good match
        matching_row = df_unused[df_unused['Sent_From'] == best_match[0]]
        if not matching_row.empty:
            matching_index = matching_row.index[0]
            df.loc[matching_index, 'Amount'] = str(df.loc[matching_index, 'Amount'])
            if df.loc[matching_index, 'Amount'] == amount:

                df.loc[matching_index, 'Used'] = True
                logging.info(f"Record with name {name} and amount {amount} validated.")
                
         
                csv_buffer = StringIO()
                df.to_csv(csv_buffer, index=False)
                s3.put_object(Bucket=bucket_name, Key=file_key, Body=csv_buffer.getvalue())
                logging.info("CSV file updated in S3 with 'Used' set to True.")
                
                return {'status': True, "message": "Record found and validated successfully."}
            else:
                logging.warning(f"Amount mismatch for {name}. Expected: {amount}, Found: {df.loc[matching_index, 'Amount']}.")
                return {'status': False, "message": f"Amount mismatch. Expected: {amount}, Found: {df.loc[matching_index, 'Amount']}."}
    else:
        logging.warning(f"No matching name found for {name}.")
        return {'status': False, "message": f"No matching name found for {name}."}


def validator(payerName, amount, days=21):
    """

    Args:
        name (String): The name for validations.
        amount (String): amount to check for validations.

    Returns:
        Json: {status: True or False, message: description}
    """
    access_key, secret_key, bucket_name , file_key = load_s3_config("./cred.yaml")

    s3 = boto3.client(
    's3',
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key,
    region_name='us-east-1')

    result = validate_reference_by_name(payerName, amount, s3, bucket_name , file_key)
    if result["status"]:
        return result
    else:
        data_from_email = email(days)
        add_unique_rows_to_csv(data_from_email,s3, bucket_name , file_key)
        result = validate_reference_by_name(payerName, amount,s3, bucket_name , file_key)
        return result


if __name__ == "__main__":
    validator()
