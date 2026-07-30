import os
import re
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from retrieve_test import load_index
from generate_answer import generate_answer

load_dotenv()

app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Maps Slack channel ID -> which document folder/index to use
# karcher: C0BLSGCV1V1
# thai-test-kitchen-menu: C0BLSJGSPQB
# jollibee-menu: C0BLYRLEX5G
# all-johnny-docs-bot-poc: C0BM0ME075X
# tennant: C0BM2F78GLC
CHANNEL_CONFIG = {
    "C0BLSGCV1V1": {"name": "Karcher", "index_path": "documents/karcher/index.json"},
    "C0BM2F78GLC": {"name": "Tennant", "index_path": "documents/tennant/index.json"},
    "C0BLSJGSPQB": {"name": "Thai Test Kitchen", "index_path": "documents/thai-test-kitchen/index.json"},
    "C0BLYRLEX5G": {"name": "Jollibee", "index_path": "documents/jollibee-menu/index.json"}
}

# Load all configured indexes once at startup, not on every message
loaded_indexes = {}
for channel_id, config in CHANNEL_CONFIG.items():
    print(f"Loading index for #{config['name']}...")
    loaded_indexes[channel_id] = load_index(config["index_path"])

@app.event("app_mention")
def handle_app_mention(event, say):
    channel_id = event["channel"]

    if channel_id not in CHANNEL_CONFIG:
        say("This channel isn't configured with a document set yet.")
        return

    raw_text = event["text"]
    question = re.sub(r"<@[A-Z0-9]+>", "", raw_text).strip()

    if not question:
        channel_name = CHANNEL_CONFIG[channel_id]["name"]
        say(f"Ask me something about the {channel_name} documentation!")
        return

    index = loaded_indexes[channel_id]
    answer = generate_answer(question, index)
    say(answer)

if __name__ == "__main__":
    handler = SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN"))
    handler.start()