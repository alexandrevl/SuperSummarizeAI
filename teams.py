import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

def send_message(message_content):
    webhook_url = os.getenv("TEAMS_WEBHOOK_URL")
    headers = {
        'Content-Type': 'application/json'
    }
    message_payload = {
        "type": "AdaptiveCard",
        "$schema": "http://adaptivecards.io/schemas/adaptive-card.json",
        "version": "1.4",
        "body": [
            {
                "type": "TextBlock",
                "text": "${$root.title}",
                "wrap": "true"
            },
            {
                "type": "RichTextBlock",
                "inlines": [
                    {
                        "type": "TextRun",
                        "text": message_content
                    }
                ]
            }
        ]
    }
    response = requests.post(webhook_url, headers=headers, data=json.dumps(message_payload))
    response.raise_for_status()

# Main Function
if __name__ == "__main__":
    send_message('Hello from Python using Webhook!')

