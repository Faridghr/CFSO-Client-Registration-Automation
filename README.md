# Client-Registration-Automation

This project is designed to automate and streamline the client registration process for a organization. The organization, which currently uses **JotForm** for course registration, faces inefficiencies due to manual tasks such as verifying **Permanent Residency (PR) cards** and reviewing **e-transfer payment screenshots**. These time-consuming steps require significant staff resources, leading to delays and potential errors. This project addresses these challenges by developing a solution to **automate** these manual processes, ensuring accuracy and improving operational efficiency.

## Key Features and Objectives
1. **JotForm Integration & Automation:** Automating the validation and management of client registration data submitted through JotForm forms. This ensures that data is processed quickly and accurately, reducing manual data entry and the risk of errors.

2. **PR Card Verification:** Incorporating machine learning techniques to automatically verify the authenticity of PR cards. This feature will eliminate the need for staff to manually review each PR card, improving verification speed and accuracy.

3. **Payment Screenshot Validation:** Automating the process of verifying e-transfer payment screenshots submitted by clients. The system will use image recognition or other verification methods to check payment details and ensure that clients’ payments are legitimate.

4. **Automated Communication:** Implementing automated notifications for both staff and clients to ensure timely updates throughout the registration process. This reduces communication overhead and ensures that clients and staff are always informed.

## Routes
### [POST] /
**Purpose:**  
Trigger form submission data processing, validate entries, and send email notifications.

**Query Parameters:**  
- `pr_amount`: The amount PR customers need to pay.
- `normal_amount`: The amount normal customers need to pay.

**Example Endpoint:**  
`http://ip:port/?pr_amount=100&normal_amount=140`

### [POST] /getdata
**Purpose:**  
Store form submission data in a MongoDB database for testing.

**Example Endpoint:**  
`http://ip:port/getdata`

## Environment Configuration (.env)
To run the project, create a `.env` file with the following variables:

### AWS S3
```
AWS_ACCESS_KEY=Your-aws-Access-Key
AWS_SECRET_KEY=Your-aws-Secret-Key
S3_BUCKET_NAME=Your-aws-Bucket-Name
S3_FILE_KEY=Data.csv
```

### Sender Payment Notification
```
INTERAC_EMAIL=notify@payments.interac.ca
```

### OCR API Key
```
X-Api-Key=Your-api-key
```

### JotForm API Key
```
JOTFORM_API_KEY=Your-api-key
```

### Database Credentials
```
MONGO_USERNAME=Your-Username
MONGO_PASSWORD=Your-Password
MONGO_CLUSTER=[Your-Cluster-Name].pfp7w.mongodb.net
```

### Email Configuration
For sending confirmation emails and error notifications:
```
CONFIRMATION_SENDER_EMAIL=example@gmail.com
CONFIRMATION_SENDER_EMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
SPONSOR_EMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
SPONSOR_EMAIL_USER=example@gmail.com
ERROR_NOTIFICATION_EMAIL_RECIEVER=example@gmail.com
```

### OpenAI API Configuration
```
OPENAI_API_KEY=Your-Openai-api
OPENAI_API_MODEL=gpt-4-turbo
```

## How to Use
1. Configure the `.env` file with the required credentials and API keys.
2. Deploy the application to a server and expose the endpoints.
3. Integrate the endpoint URLs into JotForm's webhook settings.
4. Submit test data using the endpoints to verify functionality.

## Notes
- Ensure secure storage of the `.env` file and do not expose sensitive information.
- Use proper permissions for AWS and database access to avoid unauthorized access.
