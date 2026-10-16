from flask import Flask, request
import requests
import os
import random

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "miya_verify_123")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "")
IG_USER_ID = os.getenv("IG_USER_ID", "17841434445989115")
TELEGRAM_LINK = "https://t.me/miyaarabelle"

def get_miya_reply(user_message, username=""):
    msg_lower = user_message.lower()
    is_malayalam = any("\u0d00" <= c <= "\u0d7f" for c in user_message) or any(x in msg_lower for x in ["entha", "enth", "sugam", "chechi", "mole", "eda", "chetta", "ishttam", "vishesham"])
    is_collab = any(x in msg_lower for x in ["collab", "promotion", "paid", "shoot", "brand", "sponsor", "rate", "charge", "business", "promo"])
    
    if is_collab:
        return f"Heyy 😍 thanks for collab enquiry!\n\nFor fast reply, DM on Telegram: {TELEGRAM_LINK}\nShare brand + budget, team will reply in 2hrs! 💌"
    
    if is_malayalam:
        replies_ml = [
            f"Heyy 😍 entha vishesham! Message kandu, romba happy 💖\nOru like + comment ittal reach koodum, support cheyyamo? 🥺\nTelegram: {TELEGRAM_LINK}",
            f"Ayyo nandi! 😘 Ente latest reel kandittu oru comment idamo? ❤️\nTelegramil exclusive und: {TELEGRAM_LINK}",
            f"Hey cutie! 😘 Ella msgum vaayikkum! Story share cheyyamo? 🙏\n{TELEGRAM_LINK}"
        ]
        return random.choice(replies_ml)
    
    replies_en = [
        f"Heyy 😍 so sweet of you to msg! Thank you for love 💖\nQuick favor? Follow + share my latest reel? Helps reach a lot 🥺\nJoin me on Telegram: {TELEGRAM_LINK} ✨",
        f"Omg hi! 😘 Loved ur msg! Have u seen my latest post? Drop a comment? ❤️\nFor exclusive pics: {TELEGRAM_LINK}",
        f"Hey cutie! 💕 I read all DMs!\nSupport me: Story share + like = big help 🙏\nTelegram: {TELEGRAM_LINK}"
    ]
    return random.choice(replies_en)

def send_instagram_reply(recipient_id, message_text):
    if not PAGE_ACCESS_TOKEN:
        print("ERROR: NO PAGE_ACCESS_TOKEN SET!")
        return
    url = f"https://graph.facebook.com/v20.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {"recipient": {"id": recipient_id}, "message": {"text": message_text}}
    print(f"Sending reply to {recipient_id}")
    r = requests.post(url, params=params, json=payload)
    print(f"Reply status {r.status_code}: {r.text}")
    return r

@app.route('/')
def home():
    return "Miya AI Agent Live! Webhook: /webhook - Privacy: /privacy"

@app.route('/privacy')
def privacy():
    return """
    <h1>Privacy Policy - Miya AI Agent</h1>
    <p>Last updated: May 2026</p>
    <p>This app uses 【entity-Instagram¦canonical_name=Instagram】 API to auto-reply to DMs for @miyaarabelle. Messages are processed in real-time to generate replies. We do not store personal data permanently and do not share with third parties.</p>
    <p>Contact: 【entity-Instagram¦canonical_name=Instagram】 @miyaarabelle or https://t.me/miyaarabelle</p>
    <p>Data Deletion: DM us 'delete my data' to request deletion.</p>
    """

@app.route('/terms')
def terms():
    return "<h1>Terms of Service - Miya AI Agent</h1><p>For auto-replying to 【entity-Instagram¦canonical_name=Instagram】 DMs to improve engagement. Use at your discretion.</p>"

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
    print(f"INCOMING: {data}")
    try:
        for entry in data.get('entry', []):
            for messaging in entry.get('messaging', []):
                sender_id = messaging.get('sender', {}).get('id')
                if not sender_id:
                    continue
                if 'message' in messaging and 'text' in messaging['message']:
                    if messaging['message'].get('is_echo'):
                        continue
                    user_text = messaging['message']['text']
                    print(f"User: {user_text}")
                    reply = get_miya_reply(user_text)
                    send_instagram_reply(sender_id, reply)
    except Exception as e:
        print(f"Error: {e}")
    return "EVENT_RECEIVED", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
