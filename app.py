from flask import Flask, request
import requests
import os
import random

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "miya_verify_123")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN", "")
IG_USER_ID = os.getenv("IG_USER_ID", "17841434445989115")  # will auto-detect if empty
TELEGRAM_LINK = "https://t.me/miyaarabelle"

def get_miya_reply(user_message, username=""):
    msg_lower = user_message.lower()
    is_malayalam = any("ഀ" <= c <= "ൿ" for c in user_message) or any(x in msg_lower for x in ["entha", "enth", "sugam", "chechi", "mole", "eda", "chetta", "ishttam", "vishesham"])
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
        print("ERROR: NO PAGE_ACCESS_TOKEN SET in Render env!")
        return
    # Correct endpoint - use me/messages with token as query param
    url = f"https://graph.facebook.com/v20.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    payload = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    print(f"Sending reply to {recipient_id}: {message_text[:50]}")
    r = requests.post(url, params=params, json=payload)
    print(f"Reply status {r.status_code}: {r.text}")
    return r

@app.route('/')
def home():
    return "Miya AI Agent Live! Webhook: /webhook - Env token set: " + str(bool(PAGE_ACCESS_TOKEN))

@app.route('/webhook', methods=['GET'])
def verify():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    print(f"VERIFY attempt: mode={mode} token={token} vs {VERIFY_TOKEN}")
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print("WEBHOOK VERIFIED!")
        return challenge, 200
    return "Failed", 403

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    print(f"INCOMING WEBHOOK: {data}")
    try:
        # Instagram can send in entry[0].messaging OR entry[0].changes
        for entry in data.get('entry', []):
            # Case 1: messaging (DMs)
            for messaging in entry.get('messaging', []):
                sender_id = messaging.get('sender', {}).get('id')
                recipient_id = messaging.get('recipient', {}).get('id')
                print(f"Messaging from {sender_id} to {recipient_id}")
                if not sender_id:
                    continue
                # Avoid loop if message from self
                if 'message' in messaging and 'text' in messaging['message']:
                    # Ignore echo
                    if messaging['message'].get('is_echo'):
                        continue
                    user_text = messaging['message']['text']
                    print(f"User text: {user_text}")
                    reply = get_miya_reply(user_text)
                    send_instagram_reply(sender_id, reply)
            
            # Case 2: changes (sometimes for comments)
            for change in entry.get('changes', []):
                print(f"Change event: {change}")
    except Exception as e:
        print(f"Error handling webhook: {e}")
        import traceback
        traceback.print_exc()
    return "EVENT_RECEIVED", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))
