from services.jotForm.file_utils import process_file_uploads
from services.jotForm.id_extraction import extract_form_id, extract_submission_id

def process_request_data(data, pr_amount, normal_amount):
    """
    Processes the request data and returns structured information.

    :param data: Parsed JSON data from the request.
    :param pr_amount: The payment amount for PR status.
    :param normal_amount: The payment amount for normal status.
    :return: A dictionary with extracted and processed data.
    """
    # Extract personal information
    full_name = f"{data['q6_legalName']['first']} {data['q6_legalName']['last']}"
    email = data.get("q8_email")
    phone_number = data.get("q9_phoneNumber", {}).get("full")
    payer_full_name = f"{data['q26_payersName']['first']} {data['q26_payersName']['last']}"
    type_of_status = data.get("q29_areYou")

    # Process file uploads
    pr_file_upload_urls = process_file_uploads(data, "clearFront")
    e_transfer_file_upload_urls = process_file_uploads(data, "uploadEtransfer")

    # Determine payment and PR status
    if "Yes I am" in type_of_status:
        pr_status = True
        pr_card_number = data.get("q11_prCard")
        amount_of_payment = pr_amount  # Like: 500
    else:
        pr_status = False
        amount_of_payment = normal_amount  # Like: 546

    # Extract form and submission IDs
    form_id = extract_form_id(data.get("slug", ""))
    submission_id = extract_submission_id(e_transfer_file_upload_urls)

    # Construct the response dictionary
    return {
        'Form_ID': form_id,
        'Submission_ID': submission_id,
        'Full_Name': full_name,
        'Email': email,
        'Phone_Number': phone_number,
        'PR_Status': pr_status,
        'PR_Card_Number': pr_card_number if pr_status else None,
        'Amount_of_Payment': amount_of_payment,
        'Payer_Full_Name': payer_full_name,
        'PR_File_Upload_URLs': pr_file_upload_urls,
        'E_Transfer_File_Upload_URLs': e_transfer_file_upload_urls,
    }
