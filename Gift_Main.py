import telebot
import sqlite3
import time
from flask import Flask, jsonify, request
from flask_cors import CORS
import threading

# إعدادات البوت
TOKEN = "8604397848:AAGODTAubdLu9GqFE6pLPUpJdoV0tphWiOQ"
bot = telebot.TeleBot(TOKEN)

# إعدادات Flask (الـ API)
app = Flask(__name__)
CORS(app)

def db_query(query, params=(), fetch=False, commit=False):
    conn = sqlite3.connect('gift_shop.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    res = cursor.fetchall() if fetch else None
    if commit: conn.commit()
    conn.close()
    return res

# --- جزء الـ API لعرض الهدايا في المتجر ---
@app.route('/get_my_gifts', methods=['GET'])
def get_gifts():
    user_id = request.args.get('user_id')
    # جلب الهدايا بالصور من قاعدة البيانات
    query = "SELECT g.name, g.image_url, g.icon FROM sales s JOIN gifts g ON s.gift_id = g.id WHERE s.user_id=?"
    items = db_query(query, (user_id,), fetch=True)
    return jsonify([{"name": i[0], "image": i[1], "icon": i[2]} for i in items])

# --- أوامر البوت المعتادة ---
@bot.message_handler(commands=['start'])
def start(message):
    uid, name = message.from_user.id, message.from_user.first_name
    db_query("INSERT OR IGNORE INTO users (user_id, username, points) VALUES (?, ?, ?)", (uid, name, 0), commit=True)
    bot.reply_to(message, f"أهلاً بك يا {name} في خزانة السلطنة! 👑")

# تشغيل الـ API في خلفية البوت
def run_api():
    app.run(host='0.0.0.0', port=5000)

if __name__ == "__main__":
    threading.Thread(target=run_api).start()
    print("🚀 خادم البيانات يعمل على المنفذ 5000")
    print("🛡️ بوت السلطنة جاهز...")
    bot.polling(none_stop=True)
