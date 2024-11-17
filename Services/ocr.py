import requests
from dotenv import load_dotenv
import os
from Services.jotForm.get_image import get_image_from_url

ninja_api_key = os.getenv('NINJA_API_KEY')

def image_To_Text(imgURL):
    """
    Converts the image at img_url to text using the API.
    """
    image = get_image_from_url(imgURL)

    api_url = 'https://api.api-ninjas.com/v1/imagetotext'
    files = {'image': image}

    # Add the API key to the headers
    headers = {
        'X-Api-Key': ninja_api_key
    }
    r = requests.post(api_url, files=files, headers=headers)
    return r.json()



def conver_to_base64(image):
    pass