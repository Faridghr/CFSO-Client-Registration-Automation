from flask import Flask, request, jsonify
from flask_mail import Mail
from pymongo import MongoClient
from flask import Flask, request
from routes.validate import validate_route
from routes.getdata import getdata_route
from config import Config

app = Flask(__name__)

# Configure Flask-Mail for Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # Use 465 for SSL
app.config['MAIL_USE_TLS'] = True  # Enable TLS
app.config['MAIL_USE_SSL'] = False  # Disable SSL when using TLS
app.config['MAIL_USERNAME'] = Config.CONFIRMATION_SENDER_EMAIL
app.config['MAIL_PASSWORD'] = Config.CONFIRMATION_SENDER_EMAIL_APP_PASSWORD
app.config['MAIL_DEFAULT_SENDER'] = Config.CONFIRMATION_SENDER_EMAIL

mail = Mail(app)

# MongoDB connection setup
mongo_username = Config.MONGO_USERNAME
mongo_password = Config.MONGO_PASSWORD
mongo_cluster = Config.MONGO_CLUSTER

client = MongoClient(
    f'mongodb+srv://{mongo_username}:{mongo_password}@{mongo_cluster}/?retryWrites=true&w=majority&appName=MangoCore'
)
db = client['webhook_db'] 
collection = db['webhook_data'] 



@app.route('/',methods = ['GET'])
def main():
    x = {'Health':'Success'}
    return x

# Register routes
@app.route('/',methods = ['POST'])
def validate():
    return validate_route(mail, collection)

@app.route('/getdata',methods = ['POST'])
def getdata():
    return getdata_route(collection)


if __name__ == '__main__':
    # Run the app locally for testing
    app.run(host='0.0.0.0', port=5000, debug=True)