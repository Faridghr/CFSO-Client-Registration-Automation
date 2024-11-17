from Services.ocr import image_To_Text


def validate_pr_card(pr_status, pr_card_number, full_name, pr_file_upload_urls):
    """
    Validates the PR card information.

    :param pr_status: Boolean indicating PR status.
    :param pr_card_number: PR card number.
    :param full_name: Full name of the individual.
    :param pr_file_upload_urls: List of file URLs for the PR card.
    :param image_validator: Validator service for PR card validation.
    :return: Dictionary with PR card validation results.
    """
    result = {'PR_Success': None, 'PR_Error': None}
    if not pr_status:
        return result

    is_pr_card_valid = False
    for url in pr_file_upload_urls:
        validation = check_PR_Card(pr_card_number, full_name, url)
        if validation['success']:
            is_pr_card_valid = True
            break

    if is_pr_card_valid:
        result['PR_Success'] = True
    else:
        result['PR_Success'] = False
        result['PR_Error'] = 'PR card does not match'

    return result



def check_PR_Card(prNumber, fullName, imgURL):
    """
    Validates the PR card information by extracting text from images and comparing it with provided details.

    Parameters:
    :param pr_status (bool): Indicates whether the individual claims PR status.
    :param pr_card_number (str): The PR card number to validate.
    :param full_name (str): Full name of the individual.
    :param pr_file_upload_urls (list): List of URLs for PR card images.

    :return: dict: Validation results containing:
    - 'PR_Success' (bool): True if PR card validation is successful, False otherwise.
    - 'PR_Error' (str, optional): Error message if validation fails.
    """
    json_res = image_To_Text(imgURL)

    list_name = [name.upper() for name in fullName.split(' ')]

    # List of text items to look for
    text_looking_for = list_name + ["Government", "of", "Canada", "PERMANENT", "RESIDENT", "CARD", "CARTE"]

    text_validation = []

    # Check each item in text_looking_for against the text fields in json_res
    for item in text_looking_for:
        found = any(entry['text'] == item for entry in json_res)
        text_validation.append("true" if found else "false")


    print("PR card text_validation: ", text_validation)

    # Check if all responses are true
    text_validation_result = True if all(r == "true" for r in text_validation) else False

    if(text_validation_result):
        # List of number to look for
        number_looking_for = [prNumber]

        number_validation = []

        def normalize(text):
            return ''.join(filter(str.isdigit, text))
        
        for item in number_looking_for:
            number_validation.append("true" if normalize(item) in [normalize(entry["text"]) for entry in json_res] else "false")


        print("PR card number_validation: ", number_validation)

        # Check if all responses are true
        number_validation_result = True if all(r == "true" for r in number_validation) else False

        if(number_validation_result):
            return { 'success': True }
        else:
            return { 'success': False, 'error': 'PR card number dosn not match' }
    else:
        return { 'success': False, 'error': 'PR card text dosn not match' }