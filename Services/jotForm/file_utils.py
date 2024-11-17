def process_file_uploads(data, key):
    """
    Processes file uploads and returns the URLs as a list.
    
    :param data: Dict containing request data.
    :param key: Key to look for file uploads.
    :return: List of file upload URLs.
    """
    file_upload_urls = []
    if key in data:
        file_uploads = data[key]
        if isinstance(file_uploads, list):
            file_upload_urls = file_uploads
    return file_upload_urls
