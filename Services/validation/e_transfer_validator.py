from Services.ocr import image_To_Text
from Services.email.imapTools import IMAP
import re

def validate_e_transfer(payer_full_name, amount_of_payment, e_transfer_file_upload_urls):
    """
    Validates the e-transfer details.

    :param payer_full_name: Full name of the payer.
    :param amount_of_payment: Payment amount.
    :param e_transfer_file_upload_urls: List of file URLs for e-transfer.
    :param validator: Validator service for e-transfer validation.
    :return: Dictionary with e-transfer validation results.
    """
    result = {'E_Transfer_Success': None, 'E_Transfer_Error': None}
    if not e_transfer_file_upload_urls:
        result['E_Transfer_Success'] = False
        result['E_Transfer_Error'] = 'No e-transfer files provided'
        return result

    validation = check_eTransfer(payer_full_name, amount_of_payment, e_transfer_file_upload_urls[0])
    if validation['success']:
        result['E_Transfer_Success'] = True
    else:
        result['E_Transfer_Success'] = False
        result['E_Transfer_Error'] = validation['error']

    return result


def check_eTransfer(payerFullName, amount, imgURL):
    """
    Validates e-transfer details by extracting text from an image and matching it with email records.

    :param payer_full_name (str): Full name of the payer.
    :param amount_of_payment (float): Expected payment amount.
    :param e_transfer_file_upload_urls (list): List of URLs containing e-transfer images.

    :return: dict: Validation results with keys:
    - 'E_Transfer_Success' (bool): True if validation is successful, False otherwise.
    - 'E_Transfer_Error' (str, optional): Error message if validation fails.
    """
    json_res = image_To_Text(imgURL)

    payer_name_list = [name.upper() for name in payerFullName.split(' ')]

    reference_number_list = []
    reference_pattern = re.compile(r"\b[A-Za-z0-9]{12}\b")

    for entry in json_res:
        text = entry["text"]
        # Check for 12-character alphanumeric reference pattern
        if reference_pattern.match(text):
            reference_number_list.append(text)
    print("E-Transfer Refrence number: ", reference_number_list)

    res = IMAP.find_in_email(reference_number_list, amount)
    
    print("E-transfer validation response: ", res)

    return res