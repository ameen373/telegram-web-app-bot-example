import telebot
import firebase_admin
from firebase_admin import credentials, db
import json

# 1. إعداد الاتصال بـ Firebase باستخدام ملف المفتاح
try:
    cred = credentials.Certificate("key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://telega-io-default-rtdb.firebaseio.com'
    })
    print("✅ تم الاتصال بقاعدة البيانات السحابية بنجاح!")
except Exception as e:
    print(f"❌ خطأ في الاتصال: {e}")

# 2. إعدادات البوت
TOKEN = "8750226509:AAF3zo4Og56FJj83PyajLpxN_7lquo5NsUI"
ADMIN_ID = 549686235
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.from_user.id)
    user_name = message.from_user.first_name
    
    # تسجيل أو تحديث بيانات المستخدم في Firebase
    ref = db.reference(f'users/{user_id}')
    user_data = ref.get()
    
    if not user_data:
        ref.set({
            'name': user_name,
            'balance': 0.0,
            'role': 'user'
        })
    
    # واجهة المنصة (الرابط الذي تفتحه في WebApp)
    markup = telebot.types.InlineKeyboardMarkup()
    web_app = telebot.types.WebAppInfo("https://telega-io.vercel.app/portal.html")
    markup.add(telebot.types.InlineKeyboardButton("🌍 دخول المنصة العالمية", web_app=web_app))
    
    msg = f"مرحباً بك يا {user_name} في المنصة العالمية!\nتم ربط حسابك بالسحاب بنجاح ☁️"
    bot.send_message(message.chat.id, msg, reply_markup=markup)

# أمر للمدير للتحقق من طلبات المعلنين
@bot.message_handler(commands=['check_ads'])
def check_ads(message):
    if message.from_user.id == ADMIN_ID:
        ads_ref = db.reference('ads_requests').get()
        if not ads_ref:
            bot.reply_to(message, "📭 لا توجد طلبات إعلانية حالياً.")
            return
        
        bot.send_message(ADMIN_ID, "📋 قائمة الطلبات الجديدة:")
        for uid, ads in ads_ref.items():
            for aid, data in ads.items():
                bot.send_message(ADMIN_ID, f"👤 مستخدم: {uid}\n📝 العنوان: {data['title']}\n📄 المحتوى: {data['content']}")

print("🚀 البوت العالمي نشط الآن...")
bot.polling()
