# Docs Bot POC

[![Watch the demo video](https://img.youtube.com/vi/23-lgMneJ5U/0.jpg)](https://youtu.be/23-lgMneJ5U)

🎥 [Watch the demo on YouTube](https://www.youtube.com/watch?v=23-lgMneJ5U)

A proof-of-concept Slack bot that answers questions using only the documentation provided to it. Each Slack channel is mapped to its own folder of source documents (PDFs). The bot only answers from the documents assigned to the channel a question was asked in, and explicitly says so when the answer isn't covered.

Built as a proof of concept for internal evaluation. One bot, multiple channels, each channel scoped to its own knowledge base. Multilingual feature in Karhcer channel for our international clients/techs.

## How it works

1. PDFs are dropped into a folder under `documents/<channel-name>/`.
2. `build_index.py` extracts text from every PDF in that folder, splits it into overlapping chunks, and generates an embedding (a numerical representation of meaning) for each chunk using OpenAI's `text-embedding-3-small`. The result is saved to `documents/<channel-name>/index.json`.
3. `app.py` runs the actual Slack bot. It maps each configured Slack channel ID to its corresponding index file and loads all indexes once at startup.
4. When someone `@mentions` the bot in a configured channel, it:
    - Embeds the question
    - Finds the most relevant chunks from that channel's index via cosine similarity
    - Sends those chunks, and only those chunks, to `gpt-5.4-mini` along with a system prompt that constrains it to answer solely from the provided context
    - Replies in-channel with the answer, or with an explicit "I couldn't find that in the documentation I have access to" if the context doesn't cover the question

The bot connects to Slack over Socket Mode, so it doesn't require a publicly reachable server.

## Requirements

- Python 3.10+
- A Slack app with Socket Mode enabled and the following bot scopes: `app_mentions:read`, `chat:write`, `channels:read`
- Event Subscriptions enabled, subscribed to the `app_mention` bot event
- An OpenAI API key with billing enabled

## Setup

1. Clone the repo and create a virtual environment:

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

2. Create a `.env` file in the project root:

    ```
    SLACK_BOT_TOKEN=xoxb-...
    SLACK_APP_TOKEN=xapp-...
    OPENAI_API_KEY=sk-...
    ```

3. Add source PDFs to a folder per channel:

    ```
    documents/
      karcher/
        karcher-k5-classic-operating-manual.pdf
        karcher-k5-classic-safety-instructions.pdf
      tennant/
        tennant-t7-operator-manual.pdf
    ```

4. Build the index for each folder:

    ```bash
    python3 build_index.py documents/karcher
    python3 build_index.py documents/tennant
    ```

5. Find your Slack channel IDs:

    ```bash
    python3 find_channel_ids.py
    ```

    Copy the output directly rather than retyping it by hand — channel IDs are easy to mistranscribe (e.g. `8` vs `B`).

6. Update `CHANNEL_CONFIG` in `app.py` with the real channel IDs and matching `index_path` values.

7. Run the bot:
    ```bash
    python3 app.py
    ```
    On startup it prints one `Loading index for #<name>...` line per configured channel, followed by `⚡️ Bolt app is running!` once connected.

## Project structure

```
app.py                 # Slack bot entry point, channel routing, event handling
build_index.py          # PDF -> text -> chunks -> embeddings -> index.json
document_loader.py      # PDF text extraction and chunking logic
generate_answer.py       # Retrieval + constrained answer generation
retrieve_test.py        # Retrieval logic (cosine similarity search) + manual test script
find_channel_ids.py      # Utility to look up real Slack channel IDs
documents/<channel>/     # One folder per channel, PDFs + generated index.json
```

## Updating documents

Adding, replacing, or removing a PDF in a channel's folder does **not** take effect automatically. After changing a folder's contents:

1. Rebuild that folder's index:
    ```bash
    python3 build_index.py documents/<channel-name>
    ```
2. Restart the bot (indexes are only loaded once, at startup):
    ```bash
    python3 app.py
    ```

## Configuration notes

- `CHANNEL_CONFIG["name"]` is a display label only, it doesn't need to match anything on disk.
- `CHANNEL_CONFIG["index_path"]` must exactly match the real path to that channel's `index.json`.
- Chunk size is currently 400 characters with 80 characters of overlap (`document_loader.py`), tuned based on retrieval quality testing. Smaller chunks produced sharper, more accurate matches than the original 1000/200 default.
- The bot's Slack scopes are intentionally minimal, it can read mentions and post replies, but cannot read channel history.

## Known limitations

- Answer text uses Markdown bold (`**text**`) from the model, which Slack does not render (Slack uses single asterisks). Currently displays literal asterisks.
- Indexing is full-rebuild only; adding one new PDF re-embeds every document in that folder rather than just the new file. Fine at this scale, would need incremental indexing for a larger document set.

## Cost

Embeddings and generation both run through OpenAI's API, billed separately from any ChatGPT subscription. At this document volume, cost has been fractions of a cent for embeddings and roughly $0.003–0.004 per question asked. A hard usage limit is recommended in the OpenAI dashboard as a safety net.
