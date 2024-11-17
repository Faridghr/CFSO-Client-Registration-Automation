import requests
import json
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from PIL import Image
from io import BytesIO

load_dotenv()

api_key = os.getenv('JOTFORM_API_KEY')

def extract_image_url_from_html(html_content):
    '''
    Extracts the direct image URL from an HTML page.
    
    :param html_content (str): HTML content containing the image.
    
    :return: str: Extracted image URL.
    
    :raises: ValueError: If no image URL is found in the provided HTML.
    '''
    soup = BeautifulSoup(html_content, 'html.parser')
    img_tag = soup.find('img')
    if img_tag and 'src' in img_tag.attrs:
        return img_tag['src']
    else:
        raise ValueError("No image URL found in the provided HTML.")


# Function to download the image from the extracted URL.
def get_image_from_url(image_url):
    '''
    Downloads the image from the provided URL. If the URL points to an HTML page, 
    recursively extracts the image URL and fetches the image.
    
    :param image_url (str): URL of the image or an HTML page containing the image.
    
    :return: bytes: Image content in binary format.
    
    :raises: ValueError: If unable to handle the content type of the response.
    '''
    full_url = f"{image_url}?apiKey={api_key}"
    
    print('Retrieve image from this url: ', full_url)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
    }
    response = requests.get(full_url, headers=headers)
    content_type = response.headers.get('Content-Type', '')
    if 'image' in content_type:
        return response.content

    elif 'text/html' in content_type:
        image_page_url = extract_image_url_from_html(response.content)
        # If the extracted image URL is relative, make it absolute.
        if not image_page_url.startswith('http'):
            from urllib.parse import urljoin
            image_page_url = urljoin(image_url, image_page_url)
        # Recursively call this function with the new image URL.
        return get_image_from_url(image_page_url)
    else:
        if response.status_code == 200: # If the image format is jpg
            image = Image.open(BytesIO(response.content))
            # Step 3: Convert the PIL Image to bytes
            image_bytes = BytesIO()
            image.save(image_bytes, format='JPEG')
            image_bytes = image_bytes.getvalue()
            return image_bytes
        else:
            raise ValueError(f"Unable to handle content type: {content_type}")