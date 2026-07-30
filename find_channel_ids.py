import os
from dotenv import load_dotenv
from slack_sdk import WebClient

load_dotenv()
client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

response = client.conversations_list(types="public_channel")
for channel in response["channels"]:
    print(f"{channel['name']}: {channel['id']}")