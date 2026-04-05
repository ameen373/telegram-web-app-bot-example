    conn.commit()
    conn.close()

init_db()

# --- 2. الأوامر ---
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "✅ أهلاً بك في مصنع البوتات.\n\nأرسل توكين بوتك الآن لإنشاء نسختك الخاصة!")

@bot.message_handler(func=lambda message: ":" in message.text and len(message.text) > 20)
def handle_token(message):
    user_token = message.text
    user_id = message.chat.id
    
    # حفظ التوكين
    conn = sqlite3.connect('factory.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO user_bots (user_id, token) VALUES (?, ?)', (user_id, user_token))
    conn.commit()
    conn.close()
    
    bot.send_message(user_id, "🌟 تم استلام التوكين! جاري تشغيل بوتك...\nيمكنك الآن التحكم ببوتك وإضافة الأزرار.")
    
    # تشغيل ملف القالب لكل توكين جديد
    subprocess.Popen([sys.executable, 'template.py', user_token])

# --- 3. تشغيل البوت الأساسي ---
print("البوت الأم يعمل الآن...")
while True:
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        print(f"خطأ: {e}")
        time.sleep(5)
