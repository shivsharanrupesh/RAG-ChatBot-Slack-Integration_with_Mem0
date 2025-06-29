
import os
import time
import logging
import requests
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler

logging.basicConfig(
    filename='slack_bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

SLACK_BOT_TOKEN = os.environ.get("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.environ.get("SLACK_APP_TOKEN")
FASTAPI_URL = os.environ.get("FASTAPI_URL", "http://localhost:8000/ask")

app = App(token=SLACK_BOT_TOKEN)

def ask_backend(question, session_id):
    payload = {"question": question, "session_id": session_id}
    try:
        start_time = time.time()
        response = requests.post(FASTAPI_URL, json=payload, timeout=60)
        latency = time.time() - start_time
        response.raise_for_status()
        data = response.json()
        answer = data.get("answer", "No answer found.")
        sources = data.get("sources", [])
        retrieved_chunks = data.get("retrieved_chunks", 0)
        logging.info(f"Backend responded | Session: {session_id} | Latency: {latency:.2f}s | Chunks: {retrieved_chunks} | Answer: {answer[:80]}...")
        if sources:
            sources_text = "\n".join([f"- {src['source']} (page {src.get('page','?')})" for src in sources if src.get('source')])
            answer = f"{answer}\n\n*Sources:*\n{sources_text}\n\nWas this answer helpful? :thumbsup: :thumbsdown:"
        else:
            logging.warning(f"No sources cited for question: {question} | Session: {session_id}")
            answer = f"{answer}\n\n_No source cited. Was this answer helpful? :thumbsup: :thumbsdown:_"
        return answer
    except Exception as e:
        logging.error(f"Error contacting backend: {e}")
        return f"Error contacting backend: {e}"

@app.event("app_mention")
def handle_app_mention_events(body, say):
    event = body.get("event", {})
    user = event.get("user")
    text = event.get("text", "")
    channel = event.get("channel")
    thread_ts = event.get("ts")
    logging.info(f"Received app_mention | User: {user} | Channel: {channel} | Text: {text}")
    question = text.split('>', 1)[-1].strip() if '>' in text else text.strip()
    session_id = user
    answer = ask_backend(question, session_id)
    say(text=answer, thread_ts=thread_ts)

@app.event("message")
def handle_direct_message_events(body, say, logger):
    event = body.get("event", {})
    channel_type = event.get("channel_type")
    user = event.get("user")
    text = event.get("text", "")
    thread_ts = event.get("ts")
    if channel_type == "im" and user:
        logging.info(f"Received DM | User: {user} | Text: {text}")
        session_id = user
        answer = ask_backend(text.strip(), session_id)
        say(text=answer, thread_ts=thread_ts)

@app.event("reaction_added")
def handle_reaction_events(body, logger):
    event = body.get("event", {})
    reaction = event.get("reaction")
    user = event.get("user")
    message_ts = event.get("item", {}).get("ts")
    logging.info(f"Feedback | User: {user} | Reaction: {reaction} | MessageTS: {message_ts}")

if __name__ == "__main__":
    logging.info("Slack bot is starting...")
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
