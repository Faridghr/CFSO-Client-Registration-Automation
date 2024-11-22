from imap_tools import MailBox, AND, NOT
import logging
from datetime import datetime, timedelta
import re
import pandas as pd
from io import StringIO
from thefuzz import fuzz
from thefuzz import process
from services.database.aws_s3 import AWSService
from config import Config

class IMAP():
    
    aws_service = AWSService()
    bucket_name = Config.S3_BUCKET_NAME
    file_key = Config.S3_FILE_KEY

    sender_email = Config.INTERAC_EMAIL
    email_user = Config.SPONSOR_EMAIL_USER
    email_password = Config.SPONSOR_EMAIL_APP_PASSWORD


    @classmethod
    def test_match(clf, data):
        """
        Extracts Payer name, Amount, and Reference Number from email text data.

        Args:
            data (str): The email text from which information is extracted.

        Returns:
            tuple: A tuple containing Payer name (str), Amount (str), and Reference Number (str).
                If any information is not found, the respective value will be None.
        """
        sent_from = re.search(r"Sent From:\s*(.*)", data, re.MULTILINE)
        sent_from = sent_from.group(1).strip() if sent_from else None

        amount = re.search(r"Amount: (\$[\d,]+\.\d{2})", data)
        amount = amount.group(1) if amount else None

        reference_number = re.search(r"Reference Number: (\w+)", data)
        reference_number = reference_number.group(1) if reference_number else None
        
        return sent_from, amount, reference_number

    @classmethod
    def clean_amount(clf, text):
        text = text.replace("$",'')
        text = text.replace(",",'')
        if '.' in text:
            text = text.split('.')[0]
        return text
    
    @classmethod
    def checker(clf, in_refrence:list, in_amount:str, refrence: str, amount: str):
        """
        Args:
            in_refrence (list)
            in_amount (str)
            refrence (str)
            amount (str)

        Returns:
            Dictionary: {'success': Bool, 'error': String}
        """
        amount_check =False
        refrence_check = False

        amount_updated = clf.clean_amount(amount)
        in_amount_updated = clf.clean_amount(in_amount)

        amount_check = (amount_updated == in_amount_updated)
        refrence_check = refrence in in_refrence
        
        if amount_check and refrence_check:
            return {'success': True, 'error': ''}
        elif refrence_check:
            return {'success': False, 'error': f'The amount of payment does not match : expected{amount_updated} , found{in_amount_updated}'}
        elif amount_check:
            return {'success': False, 'error': f'The refrence number is not matching'}
        else:
            return {'success': False, 'error': f'The refrence number and amount did not match'}

    @classmethod
    def find_in_email(clf, days=44): #in_name: list(Input to check name if needed) amount example: $4,000.00 - 4,000.00 - 4000.00 - 4000 - 127.54
        """
        Args:
            1. How long should the code check the mailbox(Default 14 days).

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
            with MailBox('imap.gmail.com').login(clf.email_user, clf.email_password) as mailbox:
                # logging.info("Successfully logged in to the mailbox.")
                last_week_date = (datetime.now() - timedelta(days=days)).date()
                messages = mailbox.fetch(AND(from_=clf.sender_email, date_gte=last_week_date))

                result = []
                for msg in messages:
                    sent_from, amount, reference_number = clf.test_match(msg.text)
                    sent_from = sent_from.lower()
                    amount = clf.clean_amount(amount)
                    date = msg.date_str
                    result.append({"Reference" : reference_number , "Sent_From":sent_from, "Date":date, "Amount":amount, "Used":False})
                    logging.info(f"Processed email from {sent_from} with amount {amount} and reference number {reference_number}")

                return result

        except Exception as e:
            logging.error("An error occurred: {}".format(e))

    @classmethod
    def check_reference_in_csv(clf, reference_number, df ):
        """
        Checks if a reference number exists in the provided DataFrame.
        """
        exists = reference_number in df['Reference'].values
        logging.info(f"Checked reference number {reference_number}: {'Found' if exists else 'Not Found'}")
        return exists
    
    @classmethod
    def add_unique_rows_to_csv(clf, new_data_list):
        """
        Adds only unique rows to an existing CSV file in S3 based on ReferenceNumber.
        """
        try:
            response = clf.aws_service.s3_client.get_object(Bucket=clf.bucket_name, Key=clf.file_key)
            csv_content = response['Body'].read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_content))
            # logging.info("CSV file loaded from S3 successfully.")
        except clf.aws_service.s3_client.exceptions.NoSuchKey:
            # logging.warning("CSV file not found in S3.")
            return "CSV file not found in S3."
        
        unique_rows = []
        for data in new_data_list:
            if not clf.check_reference_in_csv(data["Reference"], df):
                unique_rows.append(data)
                # logging.info(f"Adding new row for reference number {data['Reference']}.")
            # else:
                # logging.info(f"Reference number {data['Reference']} already exists. Skipping addition.")

        if unique_rows:
            df = pd.concat([df, pd.DataFrame(unique_rows)], ignore_index=True)
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            clf.aws_service.s3_client.put_object(Bucket=clf.bucket_name, Key=clf.file_key, Body=csv_buffer.getvalue())
            logging.info("Unique rows added to CSV file in S3.")
        else:
            logging.info("No new unique rows to add.")

    @classmethod
    def validate_reference_by_name(clf, name, amount):
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
            response = clf.aws_service.s3_client.get_object(Bucket=clf.bucket_name, Key=clf.file_key) 
            csv_content = response['Body'].read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_content))
            # logging.info("CSV file loaded from S3 successfully for validation.")
        except clf.aws_service.s3_client.exceptions.NoSuchKey:
            # logging.error("CSV file not found in S3.")
            return {'success': False, "message": "CSV file not found in S3."}


        df_unused = df[df['Used'] != True]
        if df_unused.empty:
            # logging.warning("No unused records found in the CSV.")
            return {'success': False, "message": "No unused records found."}


        best_match = process.extractOne(name, df_unused['Sent_From'], scorer=fuzz.token_set_ratio)
        print(best_match[0])
        amount = clf.clean_amount(amount)

        if best_match and best_match[1] >= 95:  # Threshold for a good match
             matching_row = df_unused[df_unused['Sent_From'] == best_match[0]]
             if not matching_row.empty:
                matching_index = matching_row.index[0]
                df.loc[matching_index, 'Amount'] = str(df.loc[matching_index, 'Amount'])
                if df.loc[matching_index, 'Amount'] == amount:

                    df.loc[matching_index, 'Used'] = True
                    # logging.info(f"Record with name {name} and amount {amount} validated.")
                    
                    csv_buffer = StringIO()
                    df.to_csv(csv_buffer, index=False)
                    clf.aws_service.s3_client.put_object(Bucket=clf.bucket_name, Key=clf.file_key, Body=csv_buffer.getvalue())
                    # logging.info("CSV file updated in S3 with 'Used' set to True.")
                    
                    return {'success': True, "message": "Record found and validated successfully."}
                else:
                    # logging.warning(f"Amount mismatch for {name}. Expected: {amount}, Found: {df.loc[matching_index, 'Amount']}.")
                    return {'success': False, "message": f"Amount mismatch. Expected: {amount}, Found: {df.loc[matching_index, 'Amount']}."}
             else:
                # logging.warning(f"Amount mismatch for {name}. Expected: {amount}, Found: {df.loc[matching_index, 'Amount']}.")
                return {'success': False, "message": f"Names didn't match. Expected: {df_unused['Sent_From']}, Found: {best_match[0]}."}

        else:
            logging.warning(f"No matching name found for {name}.")
            return {'success': False, "message": f"No matching name found for {name}."}
        

    @classmethod
    def validator(clf, payerName: str, amount, days=21):
        """
        Args:
            name (String): The name for validations.
            amount (String): amount to check for validations.

        Returns:
            Json: {status: True or False, message: description}
        """
        payerName = payerName.lower()
        result = clf.validate_reference_by_name(payerName, amount)
        if result["success"]:
            return result
        else:
            data_from_email = clf.find_in_email(days)
            if data_from_email != None:
                clf.add_unique_rows_to_csv(data_from_email)
                result = clf.validate_reference_by_name(payerName, amount)
            return result


if __name__ == "__main__":
    print(IMAP.validator('MOHAJERI NAV Mohammad FARZAM', '4000')) # Give Success & Error 
