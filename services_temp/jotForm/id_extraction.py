import re

def extract_form_id(slug):
    """
    Extracts form ID from the slug.
    
    :param slug: Slug string containing form ID.
    :return: Form ID or None.
    """
    match = re.search(r'/(\d+)', slug)
    return match.group(1) if match else None

def extract_submission_id(file_upload_urls):
    """
    Extracts submission ID from file upload URLs.
    
    :param file_upload_urls: List of file upload URLs.
    :return: Submission ID or None.
    """
    if file_upload_urls:
        file_upload_url = file_upload_urls[0]
        matches = re.findall(r'\d+', file_upload_url)
        if len(matches) > 1:
            return matches[1]
    return None
