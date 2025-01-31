# NBA Event-Driven Notification System

This is an event-driven notification system for NBA game updates using **AWS Lambda**, **Amazon SES** (Simple Email Service), **SNS** (Simple Notification Service), and **EventBridge**. The system fetches real-time NBA game scores from an external API (sportsdata.io) and sends notifications via email (using SES) or SMS to users.

### **Project Overview**

The goal of this project is to create a serverless, event-driven system that fetches NBA game scores at regular intervals and notifies users about the latest game results. The system uses **AWS Lambda** to run the code, **SNS** to manage notifications, and **SES** to send emails.

### **Technologies Used**
- **AWS Lambda**: Serverless compute service for running backend code.
- **Amazon SES**: Email service used for sending game updates.
- **Amazon SNS**: Notification service to distribute updates via email and SMS.
- **AWS EventBridge**: Scheduling Lambda function executions.
- **Terraform**: Infrastructure as code for provisioning AWS resources.
- **Python 3.9**: Lambda runtime for the backend logic.
- **sportsdata.io API**: External API for fetching NBA game data.

### **Features**
- Fetches NBA game data for the current day.
- Sends real-time game updates via email or SMS.
- Uses **AWS EventBridge** to trigger the Lambda function periodically.
- Email notifications sent using **Amazon SES**.
- Infrastructure managed with **Terraform**.

### **Project Setup**

#### **1. Clone the Repository**
Clone the repository to your local machine:

```bash
git clone https://github.com/your-repo/nba-notification-system.git
``` 

```
cd nba-notification-system
```
2. Setup AWS Credentials
### You need to set up AWS credentials so the system can interact with AWS services (SES, SNS, Lambda, etc.). The recommended way to handle credentials is to use AWS IAM Roles for GitHub Actions, but if you're working locally or manually, you can configure them using the following methods:

## Option 1: Configure AWS CLI on your local machine

### Run the following command to configure your AWS credentials (this stores the credentials in the ~/.aws/credentials file):

```
aws configure
```
Provide the following details when prompted:

```
AWS Access Key ID
AWS Secret Access Key
Region (e.g., us-east-1)
```

## Option 2: Use GitHub Secrets for GitHub Actions If you are using GitHub Actions, set up the following secrets in your GitHub repository:

```
AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY
AWS_REGION (e.g., us-east-1)
SES_EMAIL (Verified sender email in SES)
RECIPIENT_EMAIL (Verified recipient email in SES)
SPORTS_API_KEY (API key for sportsdata.io)
```

## 3. Install Terraform

### If you don't have Terraform installed, you can follow the instructions in the official documentation.

## 4. Setup and Deploy Using Terraform
4.1 Initialize Terraform
Navigate to the deployment/ folder and initialize Terraform:

bash
Copy
Edit
cd deployment
terraform init
4.2 Plan the Deployment
Before applying the configuration, generate an execution plan:

bash
Copy
Edit
terraform plan -var="ses_email=your-email@example.com" -var="recipient_email=recipient-email@example.com" -var="sports_api_key=your-sports-api-key"
4.3 Apply the Deployment
Once the plan looks good, apply the changes to provision your AWS resources:

bash
Copy
Edit
terraform apply -auto-approve -var="ses_email=your-email@example.com" -var="recipient_email=recipient-email@example.com" -var="sports_api_key=your-sports-api-key"
This will create the necessary Lambda function, SNS topic, IAM roles, and other infrastructure components on AWS.

Lambda Function Code
The Lambda function fetches NBA game data and processes it to send notifications. Here is a brief overview of the lambda_function.py:

python
Copy
Edit
import os
import json
import requests
import boto3
from datetime import datetime

# Load environment variables
```
SPORTS_API_KEY = os.getenv("SPORTS_API_KEY")
SPORTS_API_URL = "https://api.sportsdata.io/v3/nba/scores/json/GamesByDate"
SES_EMAIL = os.getenv("SES_EMAIL")
SNS_TOPIC_ARN = os.getenv("SNS_TOPIC_ARN")
```
```
sns_client = boto3.client("sns")
ses_client = boto3.client("ses")

def fetch_game_data(date):
    response = requests.get(f"{SPORTS_API_URL}/{date}", headers={"Ocp-Apim-Subscription-Key": SPORTS_API_KEY})
    if response.status_code != 200:
        raise Exception(f"API Error: {response.status_code}, {response.text}")
    return response.json()

def process_game_data(data):
    messages = []
    for game in data:
        messages.append(f"{game['HomeTeam']} vs {game['AwayTeam']} | Final Score: {game['HomeTeamScore']} - {game['AwayTeamScore']}")
    return "\n".join(messages)

def send_notification(message):
    sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject="NBA Game Updates"
    )
    ```

## 5. Testing

## 5.1 Local Testing (Using AWS SAM or Local Lambda)
### To test the Lambda function locally, you can use the AWS SAM CLI. Here's how:

## Install the AWS SAM CLI following the instructions here.

## To invoke the Lambda locally, run:

```
sam local invoke "FunctionName" -e event.json
``` 

### Make sure event.json contains the necessary test event data.

## 5.2 Test Lambda in AWS Console
### To test the Lambda function in the AWS Console:

### Go to the AWS Lambda Console.
### Select your Lambda function.
### Click on Test.
## Create a new test event or use the default one to trigger the function manually.
### 5.3 Verify SNS and SES Notifications
### After triggering the Lambda function, verify that you received the game score notifications either via SNS or SES:

### Check your email for the notifications.
### Ensure that your email (SES) and phone numbers (if using SMS via SNS) are properly subscribed to the SNS Topic in the AWS Console.