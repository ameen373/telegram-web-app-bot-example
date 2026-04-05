import telebot
from telebot import types
import sqlite3

# --- الإعدادات النهائية (أمين) ---
API_TOKEN = '8240625536:AAHYjLGA2CPrEclPz7m2ak267oROumP_4og'
ADMIN_ID = 549686235
BOT_USERNAME = "Te_Ads_bot"
SUPPORT_ACCOUNT = "@Te_AdsNs_bot"
FORCE_CH = "@TTelegramApkAndroid"
TASK_CH = "@dev_Telegram_ads"
SHORT_LINK = "https://adfly.site/FilmMovies"

# أسعار المتجر
STARS_50 = 5000
STARS_100 = 9500
PREMIUM_1M = 45000

bot = telebot.TeleBot(API_TOKEN, parse_mode="HTML")
bot.remove_webhook()

def get_db():
    # استخدام اسم قاعدة بيانات موحد لتجنب أخطاء المسارات
    conn = sqlite3.connect('ameen_final_safe.db')
    return conn, conn.cursor()

def init_db():
    conn, cursor = get_db()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                      (uid INTEGER PRIMARY KEY, points INTEGER DEFAULT 10, refs INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

init_db()

def is_sub(uid):
    try:
        s = bot.get_chat_member(FORCE_CH, uid).status
        return s in ['member', 'administrator', 'creator']
    except: return False

@bot.message_handler(commands=['start'])
def start(m):
    uid = m.from_user.id
    if not is_sub(uid) and uid != ADMIN_ID:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📢 اضغط هنا للاشتراك", url=f"https://t.me/{FORCE_CH[1:]}"))
        txt = f"⚠️ يجب الاشتراك أولاً:\n{FORCE_CH}\n\nاشترك ثم أرسل /start"
        return bot.send_message(m.chat.id, txt, reply_markup=kb)

    conn, cursor = get_db()
    cursor.execute('SELECT uid FROM users WHERE uid = ?', (uid,))
    if not cursor.fetchone():
        args = m.text.split()
        if len(args) > 1 and args[1].isdigit():
            rid = int(args[1])
            if rid != uid:
                cursor.execute('UPDATE users SET points = points + 5, refs = refs + 1 WHERE uid = ?', (rid,))
                try: bot.send_message(rid, "✅ انضم شخص من رابطك! (+5 نقاط)")
                except: pass
        
        cursor.execute('INSERT INTO users (uid, points) VALUES (?, ?)', (uid, 10))
        conn.commit()
        bot.send_message(m.chat.id, "<b>🎁 حصلت على 10 نقاط هدية انضمام!</b>")
    
    conn.close()
    
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("🚀 تجميع النقاط", "👥 نظام الإحالة")
    kb.add("🌟 متجر النجوم", "💰 المحفظة")
    kb.add("🏆 المتصدرين", "📞 الدعم الفني")
    
    if uid == ADMIN_ID:
        kb.add("📊 الإحصائيات", "📢 إذاعة")
        
    bot.send_message(m.chat.id, "🌟 أهلاً بك في بوت الأرباح الرسمي!", reply_markup=kb)

@bot.message_handler(func=lambda m: True)
def handle_msg(m):
    uid = m.from_user.id
    conn, cursor = get_db()
    
    if m.text == "👥 نظام الإحالة":
        ref_link = f"https://t.me/{BOT_USERNAME}?start={uid}"
        share_url = f"https://t.me/share/url?url={ref_link}&text=اربح%20النجوم%20والمميز%20مجاناً!%20💰"
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🚀 انشر رابطك الآن", url=share_url))
        bot.send_message(m.chat.id, "<b>💰 اربح 5 نقاط عن كل صديق!</b>\nاضغط بالأسفل للمشاركة:", reply_markup=kb)

    elif m.text == "🚀 تجميع النقاط":
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("🔗 رابط الربح (20 نقطة)", url=SHORT_LINK))
        kb.add(types.InlineKeyboardButton("📢 قناة المهام", url=f"https://t.me/{TASK_CH[1:]}"))
        bot.send_message(m.chat.id, "<b>🚀 مهام الربح المتاحة حالياً:</b>", reply_markup=kb)

    elif m.text == "🌟 متجر النجوم":
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton(f"⭐ 50 نجمة ({STARS_50} نقطة)", callback_data="buy_50"))
        kb.add(types.InlineKeyboardButton(f"⭐ 100 نجمة ({STARS_100} نقطة)", callback_data="buy_100"))
        kb.add(types.InlineKeyboardButton(f"💎 تليجرام مميز ({PREMIUM_1M} نقطة)", callback_data="buy_prem"))
        bot.send_message(m.chat.id, "🛒 <b>متجر الاستبدال:</b>", reply_markup=kb)

    elif m.text == "💰 المحفظة":
        cursor.execute('SELECT points FROM users WHERE uid = ?', (uid,))
        user_data = cursor.fetchone()
        if user_data:
            p = user_data[0]
            bot.send_message(m.chat.id, f"💰 رصيدك الحالي: <b>{p}</b> نقطة.")
        else:
            bot.send_message(m.chat.id, "⚠️ لم يتم العثور على بياناتك، أرسل /start لتفعيل المحفظة.")

    elif m.text == "📊 الإحصائيات" and uid == ADMIN_ID:
        cursor.execute('SELECT COUNT(*) FROM users')
        total = cursor.fetchone()[0]
        bot.send_message(m.chat.id, f"<b>📊 إحصائيات البوت:</b>\n👥 المشتركين: {total}")

    elif m.text == "🏆 المتصدرين":
        cursor.execute('SELECT uid, refs FROM users ORDER BY refs DESC LIMIT 5')
        tops = cursor.fetchall()
        txt = "🏆 <b>أكثر 5 أشخاص دعوة للأصدقاء:</b>\n\n"
        for i, (id, r) in enumerate(tops):
            txt += f"{i+1}. <code>{str(id)[:5]}***</code> — {r} 👥\n"
        bot.send_message(m.chat.id, txt)

    elif m.text == "📞 الدعم الفني":
        bot.send_message(m.chat.id, f"📞 للتواصل مع الإدارة:\n{SUPPORT_ACCOUNT}")

    elif m.text == "📢 إذاعة" and uid == ADMIN_ID:
        msg = bot.send_message(m.chat.id, "أرسل رسالة الإذاعة:")
        bot.register_next_step_handler(msg, do_bc)

    conn.close()

def do_bc(m):
    conn, cursor = get_db()
    cursor.execute('SELECT uid FROM users')
    all_u = cursor.fetchall()
    for u in all_u:
        try: bot.send_message(u[0], m.text)
        except: pass
    bot.send_message(ADMIN_ID, "✅ تمت الإذاعة.")
    conn.close()

@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def process_buy(call):
    bot.answer_callback_query(call.id, "✅ تم تسجيل طلبك! تواصل مع الإدارة.", show_alert=True)
    bot.send_message(ADMIN_ID, f"🚨 طلب سحب: <code>{call.from_user.id}</code>\nالنوع: {call.data}")

bot.infinity_polling(timeout=30)
