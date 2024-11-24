# CFSO-Client-Registration-Automation

This project focuses on automating the client registration process for the Community Family Services of Ontario (CFSO), a non-profit organization serving East Asian-Ontarians. The existing manual workflow involves verifying Permanent Residency (PR) cards and e-transfer payment screenshots, taking up significant staff time. The proposed solution aims to streamline and automate these processes, reducing staff involvement while maintaining efficiency. Key deliverables include a system to handle registration, PR card verification, payment verification, and automated communication with both staff and clients. The project is planned for completion by November 2024 in three phases: process analysis, proof of concept, and system development.

## Features
- Automates form submission validation.
- Validates Permanent Residency (PR) card images using OCR.
- Extracts and compares e-transfer payment details with form submissions.
- Sends email notifications for both successful and failed validations.
- Stores form submission data in a MongoDB database for further analysis.

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
