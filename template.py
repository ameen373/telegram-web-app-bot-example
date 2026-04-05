import telebot
from telebot import types
import sqlite3
import sys

# استلام التوكين من الملف الأساسي
if len(sys.argv) < 2:
    sys.exit()

USER_BOT_TOKEN = sys.argv[1]
bot = telebot.TeleBot(USER_BOT_TOKEN)

# دالة لجلب الأزرار من قاعدة البيانات
def get_buttons(token):
    conn = sqlite3.connect('factory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT btn_name FROM buttons WHERE token=?", (token,))
    btns = cursor.fetchall()
    conn.close()
    return btns

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = get_buttons(USER_BOT_TOKEN)
    
    if buttons:
        for btn in buttons:
            markup.add(types.KeyboardButton(btn[0]))
        bot.send_message(message.chat.id, "مرحباً بك! هذه أزرارك المخصصة:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "مرحباً! لم يتم إضافة أزرار لهذا البوت بعد.")

@bot.message_handler(func=lambda message: True)
def handle_all(message):
    conn = sqlite3.connect('factory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT btn_reply FROM buttons WHERE token=? AND btn_name=?", (USER_BOT_TOKEN, message.text))
    result = cursor.fetchone()
    conn.close()

    if result:
        bot.send_message(message.chat.id, result[0])
    else:
        bot.send_message(message.chat.id, "هذا الزر غير موجود حالياً.")

# تشغيل البوت الفرعي
try:
    bot.infinity_polling()
except Exception as e:
    print(f"خطأ في بوت فرعي: {e}")
