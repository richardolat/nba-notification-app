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
    try:
        response = requests.get(f"{SPORTS_API_URL}/{date}", headers={"Ocp-Apim-Subscription-Key": SPORTS_API_KEY})
        if response.status_code != 200:
            raise Exception(f"API Error: {response.status_code}, {response.text}")
        return response.json()
    except Exception as e:
        print(f"Error fetching game data: {e}")
        raise

def process_game_data(data):
    messages = []
    for game in data:
        messages.append(f"{game['HomeTeam']} vs {game['AwayTeam']} | Final Score: {game['HomeTeamScore']} - {game['AwayTeamScore']}")
    return "\n".join(messages)

def send_email(message):
    try:
        response = ses_client.send_email(
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
        print(f"Email sent! Message ID: {response['MessageId']}")
    except Exception as e:
        print(f"Error sending email: {e}")
        raise

def lambda_handler(event, context):
    try:
        print("Fetching NBA game data...")
        today = datetime.now().strftime("%Y-%m-%d")
        game_data = fetch_game_data(today)
        print(f"Game data fetched: {game_data}")
        
        message = process_game_data(game_data)
        print(f"Processed game data: {message}")
        
        send_email(message)
        return {"statusCode": 200, "body": "Notification Sent via SES"}
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"statusCode": 500, "body": str(e)}

