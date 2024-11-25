from flask_mail import Message
from services.openai.openai import OpenAIService
from services.email.imapTools import IMAP
from config import Config

error_notification_email_address = Config.ERROR_NOTIFICATION_EMAIL_RECIEVER

def send_email(pr_status, mail, res):
    """
    Sends an email and updates the response dictionary with the status.

    :param pr_status: Boolean indicating PR status.
    :param email_service: Email service to create the email.
    :param mail: Mail sending service.
    :param res: Response dictionary to update with email status.
    """
    msg = create_email_message(pr_status, res)
    try:
        mail.send(msg)
        res['Email_Send'] = True
    except Exception as e:
        res['Email_Send'] = False
        res['Email_Error_Message'] = str(e)



def create_email_message(pr_status, res):
    """
    Generates an email message based on PR card and E-transfer validation results.

    :param pr_status (bool): Indicates if PR validation is required.
    :param res (dict): Response dictionary containing validation results and user details.

    :return Message: An email message object with the appropriate subject, recipients, and body.
    """
    if (pr_status and res['PR_Success'] and res['E_Transfer_Success']) or (not pr_status and res['E_Transfer_Success']):
        email_body = f"""
        Dear {res['Full_Name']},

        Thank you for registering for our course! Here are your registration details:
        - Form ID: {res['Form_ID']}
        - Submission ID: {res['Submission_ID']}
        - Full Name: {res['Full_Name']}
        - Email: {res['Email']}
        - Phone Number: {res['Phone_Number']}

        We look forward to seeing you in the course!

        Best regards,
        The Community Family Services of Ontario (CFSO)
        """
        recipients = res['Email']
        subject = 'Registration Confirmation: Welcome to Our Course!'
        
    else:
        errors = []

        if res.get('PR_Success', True) == False:
            print("I AM HERE!!!")
            errors.append(res.get('PR_Error', 'PR validation failed'))

        if res.get('E_Transfer_Success', True) == False:
            print("I AM HERE!!!")
            errors.append(res.get('E_Transfer_Error', 'E-transfer validation failed'))

        error_message = ' / '.join(errors)

        email_body = f"""
        Dear CFSO,

        An error occurred during form submission:
        - Errors: {error_message}
        - Form ID: {res['Form_ID']}
        - Submission ID: {res['Submission_ID']}
        - Full Name: {res['Full_Name']}
        - Email Address: {res['Email']}
        - Phone Number: {res['Phone_Number']}

        Please address these issues as soon as possible.

        The Customer Form Detail: https://www.jotform.com/inbox/{res['Form_ID']}/{res['Submission_ID']}

        Course Table: https://www.jotform.com/tables/{res['Form_ID']}
        """
        recipients = error_notification_email_address
        subject = 'Error in Form Submission - Action Required'

    return Message(subject=subject, recipients=[recipients], body=email_body)


def create_email_draft(res):
    try:
        # Check PR Card validation and create the corresponding message only if PR_Success is False
        pr_card_validation = ""
        if res['PR_Success'] == False:
            pr_card_validation = f"PR Card Validation: {res['PR_Success']} - Error: {res['PR_Error']}"

        # Check E-Transfer validation and create the corresponding message only if E_Transfer_Success is False
        e_transfer_validation = ""
        if res['E_Transfer_Success'] == False:
            e_transfer_validation = f"E-Transfer Validation: {res['E_Transfer_Success']} - Error: {res['E_Transfer_Error']}"

        prompt = f"""
        Generate a professional email message to inform a customer about issues with their course registration submitted to the Community Family Services of Ontario (CFSO). 

        Use the following details:
        - Customer Name: {res['Full_Name']}
        {pr_card_validation}
        {e_transfer_validation}

        Include the following:
        1. A polite introduction addressing the customer by name.
        2. A request for the customer to review and resubmit their form if needed.
        3. An offer to assist further if they have any questions or concerns.

        Sender Information:
        1. Jannelle
        2. Community Family Services of Ontario (CFSO)
        3. jleung@cfso.care
        Ensure the output is clear, concise, and customer-friendly. Output only the email content message without "subject" section.
        """
        message = OpenAIService.generate_completion(prompt)
        subject = "Action Required: Issue with Your Course Registration Form"
        send_to = res['Email']

        if IMAP.create_draft(message, subject, send_to):
            res['Email_draft'] = True
        else:
            res['Email_draft'] = False

    except Exception as e:
        res['Email_draft'] = False
        res['Email_draft_Error_Message'] = str(e)

