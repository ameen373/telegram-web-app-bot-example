import telebot
from telebot import types
import time
import os

# بيانات البوت والقناة
TOKEN = '8791154774:AAFdJ9geh3kFr6OZO-J7TESSsoyPJhpwE5Q'
CHANNEL_ID = '@TTelegramApkAndroid' 
CHANNEL_LINK = 'https://t.me/TTelegramApkAndroid'
ADMIN_USER_ID = 549686235  # تم إضافة الآيدي الخاص بك هنا ✅
ADMIN_USER_NAME = '@Te_Bit'

bot = telebot.TeleBot(TOKEN, threaded=False)

# وظيفة لحفظ مستخدم جديد في قاعدة بيانات نصية
def save_user(user_id):
    if not os.path.exists('users.txt'):
        with open('users.txt', 'w') as f: f.write("")
    with open('users.txt', 'r') as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open('users.txt', 'a') as f:
            f.write(str(user_id) + "\n")

# وظيفة التحقق من الاشتراك
def is_subscribed(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return True

@bot.message_handler(commands=['start'])
def start(message):
    save_user(message.chat.id) # حفظ المستخدم فور دخوله
    
    if not is_subscribed(message.from_user.id):
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("اشترك في القناة أولاً 📢", url=CHANNEL_LINK))
        bot.send_message(message.chat.id, "⚠️ عذراً! يجب عليك الاشتراك في القناة لاستخدام البوت.", reply_markup=markup)
    else:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add("📺 قسم المسلسلات", "📞 تواصل معنا")
        
        # إظهار زر الإذاعة لك فقط كمدير
        if message.chat.id == ADMIN_USER_ID:
            markup.add("📢 إرسال إذاعة")
            
        bot.send_message(message.chat.id, f"أهلاً بك يا {message.from_user.first_name} ✅\nالبوت جاهز لخدمتك.", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    if message.text == "📺 قسم المسلسلات":
        markup = types.InlineKeyboardMarkup()
        # يمكنك إضافة روابط قنوات مسلسلاتك هنا
        markup.add(types.InlineKeyboardButton("المؤسس عثمان ⚔️", url="https://t.me/TTelegramApkAndroid"))
        bot.send_message(message.chat.id, "اختر المسلسل الذي تود متابعته:", reply_markup=markup)
        
    elif message.text == "📞 تواصل معنا":
        bot.send_message(message.chat.id, f"👨‍💻 المطور: {ADMIN_USER_NAME}")

    # بدء عملية الإذاعة للمدير فقط
    elif message.text == "📢 إرسال إذاعة" and message.chat.id == ADMIN_USER_ID:
        msg = bot.send_message(message.chat.id, "ارسل الآن النص الذي تريد إذاعته لجميع المشتركين:")
        bot.register_next_step_handler(msg, perform_broadcast)

def perform_broadcast(message):
    if message.text == "إلغاء":
        bot.send_message(message.chat.id, "تم إلغاء الإذاعة.")
        return

    with open('users.txt', 'r') as f:
        users = f.read().splitlines()
    
    bot.send_message(message.chat.id, f"⏳ جاري الإرسال لـ {len(users)} مشترك...")
    
    success = 0
    for user in users:
        try:
            bot.send_message(user, message.text)
            success += 1
            time.sleep(0.1) # تأخير بسيط لتجنب حظر تليجرام
        except:
            continue
    
    bot.send_message(message.chat.id, f"✅ اكتملت الإذاعة!\nوصلت لـ {success} مستخدم من أصل {len(users)}.")

# تشغيل البوت مع إعادة اتصال تلقائية
print("--- البوت يعمل الآن بنجاح مع صلاحيات المدير ---")
while True:
    try:
        bot.polling(none_stop=True, timeout=60)
    except:
        time.sleep(5)
