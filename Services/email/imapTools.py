from dotenv import load_dotenv
from imap_tools import MailBox, AND, NOT
import logging
import os
from datetime import datetime, timedelta
import re


class IMAP():
    load_dotenv()
    
    sender_email = 'notify@payments.interac.ca'

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
    def find_in_email(clf, in_refrence: list,in_amount:str,days=14):#in_name: list(Input to check name if needed) amount example: $4,000.00 - 4,000.00 - 4000.00 - 4000 - 127.54
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
            email_user = os.getenv('SPONSOR_EMAIL_USER')
            email_password = os.getenv('SPONSOR_EMAIL_PASSWORD')

            with MailBox('imap.gmail.com').login(email_user, email_password) as mailbox:
                logging.info("Successfully logged in to the mailbox.")
                last_week_date = (datetime.now() - timedelta(days=days)).date()
                messages = mailbox.fetch(AND(from_=clf.sender_email, date_gte=last_week_date))

                for msg in messages:
                    sent_from, amount, reference_number = clf.test_match(msg.text)
                    logging.info(f"Processed email from {sent_from} with amount {amount} and reference number {reference_number}")
                    
                    #TODO: Check if the reference_number is not in the database countinue

                    result = clf.checker(in_refrence,in_amount, reference_number, amount)

                    if result['success']:
                        # mailbox.add_gmail_label(msg.uid, 'Processed')
                        #TODO: Store reference_number in database
                        break

                return result

        except Exception as e:
            logging.error("An error occurred: {}".format(e))

if __name__ == "__main__":
    print(IMAP.find_in_email(['Reference','C1APJDfjFfZu','MOHAJERI'], '4000'))