from flask import Flask, request
import requests
import os
import random
from datetime import datetime

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "miya_verify_123")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "")
IG_USER_ID = "17841434445989115"
TELEGRAM_LINK = "https://t.me/miyaarabelle"

def get_miya_reply(user_message, username=""):
    msg_lower = user_message.lower()
    is_malayalam = any("\u0d00" <= c <= "\u0d7f" for c in user_message) or any(x in msg_lower for x in ["entha", "enth", "sugam", "chechi", "mole", "eda", "chetta", "ishttam"])
    is_collab = any(x in msg_lower for x in ["collab", "promotion", "paid", "shoot", "brand", "sponsor", "rate", "charge", "business", "promo"])
    
    if is_collab:
        return f"Heyy 😍 thanks for collab enquiry!\n\nFor fast reply, DM on Telegram: {TELEGRAM_LINK}\nShare brand + budget, team will reply in 2hrs! 💌"
    
    if is_malayalam:
        replies_ml = [
            f"Heyy 😍 entha vishesham! Message kandu, romba happy 💖\nOru like + comment ittal reach koodum, support cheyyamo? 🥺\nTelegram: {TELEGRAM_LINK}",
            f"Ayyo nന്ദി {username}! 😘 Ente latest reel kandittu oru comment idamo? ❤️\nTelegramil exclusive und: {TELEGRAM_LINK}",
            f"Hey cutie! 😘 Ella msgum vaayikkum! Story share cheyyamo? 🙏\n{TELEGRAM_LINK}"
        ]
        return random.choice(replies_ml)
    
    replies_en = [
        f"Heyy {username} 😍 so sweet of you to msg! Thank you for love 💖\nQuick favor? Follow + share my latest reel? Helps reach a lot 🥺\nJoin me on Telegram: {TELEGRAM_LINK} ✨",
        f"Omg hi {username}! 😘 Loved ur msg! Have u seen my latest post? Drop a comment? ❤️\nFor exclusive pics: {TELEGRAM_LINK}",
        f"Hey cutie {username}! 💕 I read all DMs!\nSupport me: Story share + like = big help 🙏\nTelegram: {TELEGRAM_LINK}"
    ]
    return random.choice(replies_en)

def send_instagram_reply(recipient_id, message_text):
    if not PAGE_ACCESS_TOKEN:
        print("NO TOKEN SET")
        return
    url = f"https://graph.facebook.com/v20.0/{IG_USER_ID}/messages"
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}, "access_token": PAGE_ACCESS_TOKEN}
    r = requests.post(url, json=payload)
    print(f"Reply status {r.status_code}: {r.text}")

@app.route('/')
def home():
    return "Miya AI Agent Live! Webhook: /webhook"

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return challenge, 200
    return "Failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(data)
    try:
        for entry in data.get('entry', []):
            for messaging in entry.get('messaging', []):
                sender_id = messaging.get('sender', {}).get('id')
                if sender_id == IG_USER_ID:
                    continue
                if 'message' in messaging and 'text' in messaging['message']:
                    user_text = messaging['message']['text']
                    reply = get_miya_reply(user_text)
                    send_instagram_reply(sender_id, reply)
    except Exception as e:
        print(f"Error: {e}")
    return "EVENT_RECEIVED", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
