import requests
import os
import logging
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()  # Carrega as variáveis do arquivo .env

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

ACCESS_TOKEN = os.environ.get('INSTAGRAM_ACCESS_TOKEN')
VERIFY_TOKEN = os.environ.get('WEBHOOK_VERIFY_TOKEN')

def handle_message(sender_id, message_text):
    # Implemente a lógica do seu chatbot aqui
    response = f"Recebi sua mensagem: {message_text}. Como posso ajudar?"
    send_message(sender_id, response)

def send_message(recipient_id, message_text):
    params = {
        "access_token": ACCESS_TOKEN
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    }
    try:
        r = requests.post("https://graph.facebook.com/v16.0/me/messages", params=params, headers=headers, json=data)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        logging.error(f"Failed to send message: {e}")

@app.route('/', methods=['GET'])
def verify():
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return "Hello World!", 200

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    logging.info(f"Received webhook data: {data}")
    if data.get("object") == "instagram":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                sender_id = messaging_event.get("sender", {}).get("id")
                if messaging_event.get("message"):
                    message_text = messaging_event["message"].get("text")
                    if sender_id and message_text:
                        handle_message(sender_id, message_text)
    return "ok", 200

if __name__ == '__main__':
    app.run(debug=True)