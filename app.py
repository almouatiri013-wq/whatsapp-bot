import os
from flask import Flask, request
import requests

app = Flask(__name__)

PHONE_ID = "1488894340965603"
TOKEN = os.environ.get("TOKEN", os.environ.get("WHATSAPP_TOKEN", ""))
VERIFY_TOKEN = "mystore123"

@app.route("/", methods=["GET"])
@app.route("/whatsapp/", methods=["GET"])
@app.route("/whatsapp/healthz", methods=["GET"])
def home():
    return "WhatsApp Bot is Running ✅ - My Store Bot - health OK", 200

@app.route("/webhook", methods=["GET"])
@app.route("/whatsapp/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

@app.route("/webhook", methods=["POST"])
@app.route("/whatsapp/webhook", methods=["POST"])
def webhook():
    data = request.get_json(silent=True) or {}
    try:
        entry = data.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {})
        if "messages" in entry:
            phone = entry["messages"][0]["from"]
            msg = entry["messages"][0].get("text", {}).get("body", "").lower()
            
            if any(x in msg for x in ["مرحبا","السلام","هلا","hi","hello"]):
                reply = "هلا والله حياك في متجري 👋\n\n1️⃣ شوف المنتجات\n2️⃣ اسعار الجملة\n3️⃣ تواصل معنا"
            elif "1" in msg or "منتجات" in msg:
                reply = "🛒 منتجاتنا:\n\n• ساعات ذكية - 99 ريال\n• سماعات - 79 ريال\n• كفرات - 29 ريال\n\nاكتب رقم المنتج للطلب"
            elif "2" in msg or "جملة" in msg:
                reply = "💰 اسعار الجملة:\n\n• 10 حبات فأكثر خصم 20%\n• 50 حبة فأكثر خصم 35%\n\nتواصل: 05xxxxxxxx"
            else:
                reply = "ما فهمت، اكتب 'مرحبا' لبدء القائمة 🙂"
            
            if TOKEN:
                url = f"https://graph.facebook.com/v19.0/{PHONE_ID}/messages"
                headers = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}
                payload = {
                    "messaging_product": "whatsapp",
                    "to": phone,
                    "type": "text",
                    "text": {"body": reply}
                }
                requests.post(url, json=payload, headers=headers, timeout=10)
    except Exception as e:
        print(f"Error: {e}")
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
