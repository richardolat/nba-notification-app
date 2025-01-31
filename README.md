# NBA Event-Driven Notification System

This is an event-driven notification system for NBA game updates using **AWS Lambda**, **Amazon SES** (Simple Email Service), **SNS** (Simple Notification Service), and **EventBridge**. The system fetches real-time NBA game scores from an external API (sportsdata.io) and sends notifications via email (using SES) or SMS to users.

## Project Overview

The goal of this project is to create a serverless, event-driven system that fetches NBA game scores at regular intervals and notifies users about the latest game results. The system uses **AWS Lambda** to run the code, **SNS** to manage notifications, and **SES** to send emails. This is part of **Day 2 of the 30 Days of DevOps Challenge**, where I focus on automating processes in a serverless architecture using AWS services.

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

### **SES Permissions**
In order to send emails through Amazon SES, the Lambda function assumes an IAM role with the necessary permissions. Specifically, the IAM role needs to allow the `ses:SendEmail` and `ses:SendRawEmail` actions. Below is the policy added to the Lambda IAM role for sending emails via SES:

```hcl
resource "aws_iam_role_policy" "lambda_ses_permissions" {
  name = "lambda_ses_permissions"
  role = aws_iam_role.lambda_execution.id

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ],
        Resource = "*"
      }
    ]
  })
}
This policy allows the Lambda function to send both regular emails (ses:SendEmail) and raw emails (ses:SendRawEmail) via SES.

Project Setup
1. Clone the Repository
Clone the repository to your local machine:

```bash
git clone https://github.com/your-repo/nba-notification-system.git
cd nba-notification-system
```
## 2. Setup AWS Credentials
### You need to set up AWS credentials so the system can interact with AWS services (SES, SNS, Lambda, etc.). The recommended way to handle credentials is to use AWS IAM Roles for GitHub Actions, but if you're working locally or manually, you can configure them using the following methods:

### Option 1: Configure AWS CLI on your local machine
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
## Option 2: Use GitHub Secrets for GitHub Actions
### If you're using GitHub Actions, set up the following secrets in your GitHub repository:
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
### Initialize Terraform
### Navigate to the deployment folder and initialize Terraform:

```
cd terraform
terraform init
```
### Plan the Deployment
### Before applying the configuration, generate an execution plan:

```
terraform plan -var="ses_email=your-email@example.com" -var="recipient_email=recipient-email@example.com" -var="sports_api_key=your-sports-api-key"
```
## Apply the Deployment
### Once the plan looks good, apply the changes to provision your AWS resources:

```
terraform apply -auto-approve -var="ses_email=your-email@example.com" -var="recipient_email=recipient-email@example.com" -var="sports_api_key=your-sports-api-key"
```
### This will create the necessary Lambda function, SNS topic, IAM roles, and other infrastructure components on AWS.

## Lambda Function Code
### The Lambda function fetches NBA game data and processes it to send notifications. Here is a brief overview of the ```lambda_function.py:```


```python
import os
import json
import requests
import boto3
from datetime import datetime

# Load environment variables
SPORTS_API_KEY = os.getenv("SPORTS_API_KEY")
SPORTS_API_URL = "https://api.sportsdata.io/v3/nba/scores/json/GamesByDate"
SES_EMAIL = os.getenv("SES_EMAIL")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")

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

def send_email(message):
    ses_client.send_email(
        Source=SES_EMAIL,
        Destination={
            "ToAddresses": [RECIPIENT_EMAIL],
        },
        Message={
            "Subject": {
                "Data": "NBA Game Updates",
                "Charset": "UTF-8"
            },
            "Body": {
                "Text": {
                    "Data": message,
                    "Charset": "UTF-8"
                }
            }
        }
    )

def lambda_handler(event, context):
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        game_data = fetch_game_data(today)
        message = process_game_data(game_data)
        send_email(message)
        return {"statusCode": 200, "body": "Notification Sent via SES"}
    except Exception as e:
        return {"statusCode": 500, "body": str(e)}
```

## Testing the Lambda Function
### Once you have deployed everything, you can manually trigger the Lambda function via the AWS Console to ensure it fetches NBA scores and sends notifications.

### Monitoring and Logs
### You can monitor the Lambda function's execution and check for any issues in the CloudWatch Logs:

### Go to CloudWatch Console.
### Navigate to Logs > Log Groups.
### Look for logs related to the Lambda function (/aws/lambda/nba_notification_function).

## Conclusion
### This project provides an automated event-driven system that fetches real-time NBA game scores and notifies users via email using SES. It was built as part of Day 2 of the 30 Days of DevOps challenge.

### Feel free to explore, modify, and build on this as you continue your DevOps journey. If you have any issues or feedback, don’t hesitate to raise an issue or contact me!


