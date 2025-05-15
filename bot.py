from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import json
import os

LIST_FILE = "list.json"

def load_list():
    if os.path.exists(LIST_FILE):
        with open(LIST_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_list(data):
    with open(LIST_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)



app = Flask(__name__)
shopping_list = []

@app.before_request
def log_request_info():
    print("📥 Request received")
    print("Headers:", request.headers)
    print("Body:", request.get_data())

@app.route("/bot", methods=["POST"])
def bot():
    try:
        incoming_msg = request.values.get("Body", "").strip().lower()
        print("User message:", incoming_msg)

        resp = MessagingResponse()
        msg = resp.message()

        shopping_list = load_list()

        if incoming_msg.startswith("הוסף "):
            item = incoming_msg[5:]
            shopping_list.append(item)
            save_list(shopping_list)
            msg.body(f"הוספתי את '{item}' לרשימת הקניות שלך.")
        elif incoming_msg == "רשימה":
            if shopping_list:
                msg.body("📋 רשימת הקניות שלך:\n" + "\n".join(f"- {item}" for item in shopping_list))
            else:
                msg.body("הרשימה שלך ריקה.")
        elif incoming_msg == "נקה":
            shopping_list.clear()
            save_list(shopping_list)
            msg.body("הרשימה נוקתה.")
        elif incoming_msg.startswith("הסר "):
            del_item = incoming_msg[4:]
            if del_item not in shopping_list:
                msg.body(f"הפריט '{del_item}' לא נמצא ברשימה.")
                return str(resp)
            shopping_list.remove(del_item)
            save_list(shopping_list)
            msg.body(f"הסרתי את '{del_item}' מהרשימה.")
        else:
            msg.body("שלח:\n• הוסף <פריט>\n• רשימה\n• נקה\n• הסר <פריט>\n\nלרשימת הקניות שלך.")

        return str(resp)

    except Exception as e:
        print("❌ שגיאה:", e)
        return "Error: " + str(e), 500


if __name__ == "__main__":
   port = int(os.environ.get("PORT", 5000))
app.run(host="0.0.0.0", port=port)


