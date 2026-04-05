import telebot
import os
import subprocess

# 1. إعدادات البوت (التوكن والأيدي الخاص بك)
TOKEN = '8581827609:AAGzos0IREbVSKXcyNKcL-rnL1RXsO1oUeY'
ADMIN_ID = 549686235

bot = telebot.TeleBot(TOKEN)

print("✅ البوت يعمل الآن بنجاح يا أمين... اذهب لتليجرام وأرسل الصورة.")

# 2. أمر البداية
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id == ADMIN_ID:
        bot.reply_to(message, "أهلاً بك يا مطورنا أمين 🛡️\nأرسل لي صورة (الجنبية أو السيف) وسأحولها فوراً إلى هدية رقمية WEBM.")
    else:
        bot.reply_to(message, "عذراً، هذا البوت مخصص للمطور أمين فقط.")

# 3. محرك استقبال وتحويل الصور
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.from_user.id != ADMIN_ID:
        return

    try:
        # إشعار المستخدم ببدء العمل
        msg = bot.reply_to(message, "⚙️ جاري معالجة الهدية الملكية... (تحجيم وتنسيق WEBM)")

        # تحميل الصورة من سيرفرات تليجرام
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        with open("input.jpg", 'wb') as new_file:
            new_file.write(downloaded_file)

        # تحويل الصورة باستخدام ffmpeg (المقاس الرسمي للهدايا 512x512)
        # الأمر يقوم بجعل الصورة فيديو مدته 3 ثواني وبدون صوت وبصيغة متوافقة
        cmd = "ffmpeg -i input.jpg -vf 'scale=512:512' -c:v libvpx-vp9 -pix_fmt yuva420p -an -t 3 output.webm -y"
        subprocess.run(cmd, shell=True)

        # التأكد من نجاح عملية التحويل وإرسال الملف
        if os.path.exists("output.webm"):
            with open("output.webm", 'rb') as video_sticker:
                bot.send_document(message.chat.id, video_sticker, caption="✅ تم التحويل بنجاح!\n\nالآن ارفع هذا الملف إلى @Stickers كـ 'Video Sticker' لتفعيله كهدية.")
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text("❌ فشل التحويل. تأكد من تثبيت ffmpeg عبر الأمر:\npkg install ffmpeg", message.chat.id, msg.message_id)

        # تنظيف الذاكرة وحذف الملفات المؤقتة
        if os.path.exists("input.jpg"): os.remove("input.jpg")
        if os.path.exists("output.webm"): os.remove("output.webm")

    except Exception as e:
        bot.reply_to(message, f"❌ حدث خطأ فني: {e}")

# تشغيل البوت المستمر
bot.polling(none_stop=True)
