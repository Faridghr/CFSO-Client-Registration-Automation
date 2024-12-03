import requests
from dotenv import load_dotenv
import os
from services.jotForm.get_image import get_image_from_url
import boto3
from config import Config

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



def image_To_Text_Local_Model(imgURL):
    """
    Converts the image at img_url to text using our local model.
    """
    image = get_image_from_url(imgURL)

    api_url = 'http://54.81.146.167:5000/extract-text'
    
    files = {'file': ('image.jpg', image, 'image/jpeg')}

    r = requests.post(api_url, files=files)
    return r.json()


def image_To_Text_aws_textract(imgURL):
    """
    Converts the image at img_url to text using aws texteract.
    """
    textract = boto3.client(
        'textract',
        aws_access_key_id=Config.AWS_ACCESS_KEY,
        aws_secret_access_key=Config.AWS_SECRET_KEY,
        region_name='us-east-1'
    )

    image = get_image_from_url(imgURL)

    response = textract.detect_document_text(
        Document={'Bytes': image}
    )
    
    result = [{'text': word} for block in response['Blocks'] if block['BlockType'] == 'LINE'
              for word in block.get('Text', '').split()]
   
    return result


# url = 'https://www.jotform.com/uploads/javanroodiz/243138058138255/6070135805971446099/card.jpg'
# print(image_To_Text_Local_Model(url))

# python -m services.ocr