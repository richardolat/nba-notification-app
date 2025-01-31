import os
import json
import requests
import boto3
from datetime import datetime

# Load environment variables
SPORTS_API_KEY = os.getenv("SPORTS_API_KEY")
SPORTS_API_URL = "https://api.sportsdata.io/v3/nba/scores/json/GamesByDate"
SES_EMAIL = os.getenv("SES_EMAIL")  # Verified sender email
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL")  # Verified recipient email

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
