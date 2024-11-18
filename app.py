from flask import Flask, request, jsonify
from flask_mail import Mail
from pymongo import MongoClient
import os
from flask import Flask, request
from routes.validate import validate_route
from routes.getdata import getdata_route

app = Flask(__name__)

# Configure Flask-Mail for Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Use 465 for SSL
app.config['MAIL_USE_TLS'] = True  # Enable TLS
app.config['MAIL_USE_SSL'] = False  # Disable SSL when using TLS
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER')  # Your Gmail address
app.config['MAIL_PASSWORD'] = os.getenv('GMAIL_APP_PASSWORD')  # Your Gmail password
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER')  # Default sender

mail = Mail(app)

# MongoDB connection setup
mongo_username = os.getenv('MONGO_USERNAME')
mongo_password = os.getenv('MONGO_PASSWORD')
mongo_cluster = os.getenv('MONGO_CLUSTER')
client = MongoClient(
    f'mongodb+srv://{mongo_username}:{mongo_password}@{mongo_cluster}/?retryWrites=true&w=majority&appName=MangoCore'
)
db = client['webhook_db'] 
collection = db['webhook_data'] 


@app.route('/',methods = ['GET'])
def main():
    x = {'Health':'True'}
    return x

# Register routes
app.add_url_rule('/', view_func=validate_route(mail, collection), methods=['POST'])

app.add_url_rule('/getdata', view_func=getdata_route(collection), methods=['POST'])


if __name__ == '__main__':
    # Run the app locally for testing
    app.run(host='0.0.0.0', port=5000, debug=True)