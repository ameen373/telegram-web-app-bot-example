import telebot
import sqlite3
import os
import subprocess
from telebot import types

# --- إعدادات الحساب الخاصة بك ---
TOKEN = '8795025264:AAHi-QPGm36tJsxqTVkcfaSrOOSRXm1ooQY'
ADMIN_ID = 549686235
GH_TOKEN = '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'
GH_EMAIL = 'ameen.alezi2013@gmail.com'
GH_USER = 'ameen373'
REPO_NAME = 'my-gifts-store'

bot = telebot.TeleBot(TOKEN)

# تهيئة قاعدة البيانات والتكوين الأولي لـ Git
def setup_environment():
    conn = sqlite3.connect('gifts_factory.db')
    conn.execute('''CREATE TABLE IF NOT EXISTS orders (user_id INTEGER, gift_name TEXT, price INTEGER, status TEXT)''')
    conn.close()
    # إعداد هوية المستخدم في تيرمكس لتجنب أخطاء الرفع
    subprocess.run(f'git config --global user.email "{GH_EMAIL}"', shell=True)
    subprocess.run(f'git config --global user.name "{GH_USER}"', shell=True)

setup_environment()

def update_and_push_web():
    conn = sqlite3.connect('gifts_factory.db')
    cursor = conn.cursor()
    cursor.execute("SELECT gift_name, price FROM orders")
    rows = cursor.fetchall()
    conn.close()

    html_content = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Gifts Store</title>
        <style>
            body {{ background-color: #18222d; color: white; font-family: sans-serif; text-align: center; padding: 20px; }}
            .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; }}
            .card {{ background: #212d3b; border-radius: 15px; padding: 15px; border: 1px solid #2f3e4e; }}
            .price {{ color: #fecb2e; font-size: 18px; font-weight: bold; }}
        </style>
    </head>
    <body>
        <h2>💎 معرض أمين للمقتنيات الملكية</h2>
        <div class="grid">
    """
    for row in rows:
        html_content += f"""
        <div class="card">
            <img src="https://via.placeholder.com/150/248bcf/ffffff?text={row[0]}" style="width:100%; border-radius:10px;">
            <div style="margin: 10px 0;">{row[0]}</div>
            <div class="price">⭐️ {row[1]}</div>
        </div>"""
    
    html_content += "</div></body></html>"

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html_content)

    # أوامر الرفع التلقائي لـ GitHub
    remote_url = f"https://{GH_TOKEN}@github.com/{GH_USER}/{REPO_NAME}.git"
    subprocess.run("git add index.html", shell=True)
    subprocess.run('git commit -m "تحديث تلقائي للمتجر عبر البوت"', shell=True)
    subprocess.run(f"git push {remote_url} main", shell=True)
    print("🚀 تم تحديث الموقع بنجاح!")

@bot.message_handler(commands=['start'])
def welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('🎁 المعرض', '🛠️ صنع هدية')
    bot.reply_to(message, "🛡️ النظام جاهز. الموقع سيُحدث تلقائياً عند إضافة أي هدية.", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == '🛠️ صنع هدية')
def ask_photo(message):
    bot.reply_to(message, "📸 أرسل صورة الهدية.")

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.from_user.id == ADMIN_ID:
        msg = bot.reply_to(message, "📝 اسم الهدية؟")
        bot.register_next_step_handler(msg, lambda m: ask_price(m, message.photo[-1].file_id))

def ask_price(message, photo_id):
    gift_name = message.text
    msg = bot.reply_to(message, f"💰 سعر '{gift_name}'؟")
    bot.register_next_step_handler(msg, lambda m: process_all(m, photo_id, gift_name))

def process_all(message, photo_id, gift_name):
    try:
        price = int(message.text)
        bot.send_message(message.chat.id, "⚙️ جاري التحويل والرفع للموقع...")
        
        # معالجة الصورة
        file_info = bot.get_file(photo_id)
        downloaded_file = bot.download_file(file_info.file_path)
        with open("input.jpg", 'wb') as f: f.write(downloaded_file)
        subprocess.run("ffmpeg -i input.jpg -vf 'scale=512:512' -c:v libvpx-vp9 -pix_fmt yuva420p -an -t 3 output.webm -y", shell=True)

        # الحفظ والرفع
        conn = sqlite3.connect('gifts_factory.db')
        conn.execute("INSERT INTO orders VALUES (?, ?, ?, ?)", (message.chat.id, gift_name, price, "Done"))
        conn.commit()
        conn.close()

        update_and_push_web() # تحديث الموقع ورفعه لـ GitHub

        with open("output.webm", 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"✅ {gift_name}\n💰 ⭐️ {price}\n🌐 تم تحديث الموقع!")
            
    except Exception as e:
        bot.reply_to(message, f"⚠️ خطأ: {e}")

bot.polling(none_stop=True)
