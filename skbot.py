import telebot
from telebot import types
import sqlite3
import requests
import time

# --- بياناتك الأساسية ---
BOT_TOKEN = '8720149324:AAHFgl0FhtQ2enSa6taEySgp92mIlwoLSXo'
CRYPTO_TOKEN = '561833:AAxy3UTMtBCA3fAOB6UVBLij2aCOXWPvN0h'
ADMIN_ID = 549686235
CHANNEL_ID = "@TTelegramApkAndroid"
CHANNEL_URL = "https://t.me/TTelegramApkAndroid"

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="Markdown")

# --- قائمة المسلسلات ---
SERIES_LIST = {
    "انت من احببت": "https://t.me/+mzg5JHHDG4E1NGQ0",
    "ورود وذنوب": "https://t.me/+bQdsnou-d-A2NTE0",
    "تحت الارض": "https://t.me/+Fdc1VH99ucUxM2Rk",
    "المدينة البعيدة": "https://t.me/+V3fENg80ScYxODZk",
    "حلم اشرف": "https://t.me/+-9Npv2v2Im9lMjFk",
    "العائلة هي الامتحان اخي": "https://t.me/+Zw2VD5ebBgZhM2Q8"
}

# --- إعداد قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('sk_final_v3.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (user_id INTEGER PRIMARY KEY, points INTEGER DEFAULT 0, 
                 referred_by INTEGER, joined_at TEXT)''')
    conn.commit()
    return conn

db_conn = init_db()

def get_user_data(user_id):
    c = db_conn.cursor()
    c.execute("SELECT points, referred_by, joined_at FROM users WHERE user_id = ?", (user_id,))
    return c.fetchone()

def register_user(user_id, ref_id=None):
    if not get_user_data(user_id):
        c = db_conn.cursor()
        c.execute("INSERT INTO users (user_id, points, referred_by, joined_at) VALUES (?, 10, ?, ?)", 
                  (user_id, ref_id, time.strftime("%Y-%m-%d")))
        db_conn.commit()
        return True
    return False

def add_points(user_id, amount):
    c = db_conn.cursor()
    c.execute("UPDATE users SET points = points + ? WHERE user_id = ?", (amount, user_id))
    db_conn.commit()

def is_subscribed(user_id):
    try:
        status = bot.get_chat_member(CHANNEL_ID, user_id).status
        return status in ['member', 'administrator', 'creator']
    except: return False

def main_kb(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("📺 قائمة المسلسلات", callback_data="view_series"),
        types.InlineKeyboardButton("💰 شراء النقاط", callback_data="buy_points_main"),
        types.InlineKeyboardButton("🔗 نظام الإحالة", callback_data="referral_info"),
        types.InlineKeyboardButton("👤 حسابي", callback_data="my_profile"),
        types.InlineKeyboardButton("✨ لماذا تختارنا؟", callback_data="about_us")
    )
    if user_id == ADMIN_ID:
        markup.add(
            types.InlineKeyboardButton("📊 الإحصائيات", callback_data="adm_stats"),
            types.InlineKeyboardButton("📢 إذاعة", callback_data="adm_broadcast"),
            types.InlineKeyboardButton("➕ شحن يدوي", callback_data="adm_add_pts")
        )
    return markup

# --- الأوامر ---
@bot.message_handler(commands=['start'])
def start_cmd(message):
    user_id = message.from_user.id
    args = message.text.split()
    ref_id = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
    
    if register_user(user_id, ref_id):
        if ref_id and ref_id != user_id:
            add_points(ref_id, 10)
            try: bot.send_message(ref_id, "🎉 سجل مستخدم جديد من رابطك وحصلت على 10 نقاط!")
            except: pass

    if not is_subscribed(user_id):
        kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("✅ اشترك هنا", url=CHANNEL_URL))
        kb.add(types.InlineKeyboardButton("🔄 تم الاشتراك", callback_data="main_menu"))
        return bot.send_message(user_id, "⚠️ *يجب الاشتراك أولاً لتفعيل البوت واستلام هدية الـ 10 نقاط!*", reply_markup=kb)

    data = get_user_data(user_id)
    bot.send_message(user_id, f"🎬 *مرحباً بك*\n💰 رصيدك: `{data[0]}` نقطة", reply_markup=main_kb(user_id))

# --- معالجة الأزرار ---
@bot.callback_query_handler(func=lambda call: True)
def callback_manager(call):
    user_id = call.from_user.id
    
    if call.data == "main_menu":
        data = get_user_data(user_id)
        bot.edit_message_text(f"🏠 *القائمة الرئيسية*\n💰 رصيدك: `{data[0]}` نقطة", user_id, call.message.message_id, reply_markup=main_kb(user_id))

    elif call.data == "about_us":
        msg = ("🛡️ *لماذا تثق بنا؟*\n\n"
               "✅ *نظام آلي:* جميع عمليات الشحن بالنجوم و USDT تتم برمجياً وفورياً.\n"
               "✅ *دعم مستمر:* نحن متواجدون لمساعدتك في حال واجهت أي مشكلة.\n"
               "✅ *شفافية:* يمكنك رؤية رصيدك وتاريخ انضمامك بوضوح.\n"
               "✅ *تحديثات:* نقوم بإضافة أحدث المسلسلات بشكل دوري.\n\n"
               "🌟 هدفنا توفير أفضل تجربة مشاهدة آمنة وسريعة.")
        kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="main_menu"))
        bot.edit_message_text(msg, user_id, call.message.message_id, reply_markup=kb)

    elif call.data == "buy_points_main":
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(
            types.InlineKeyboardButton("💵 شحن USDT (تلقائي)", callback_data="usdt_list"),
            types.InlineKeyboardButton("⭐ شحن نجوم (تلقائي)", callback_data="stars_list"),
            types.InlineKeyboardButton("🟡 Binance Pay (يدوي)", callback_data="pay_binance"),
            types.InlineKeyboardButton("⬅️ رجوع", callback_data="main_menu")
        )
        bot.edit_message_text("💰 *طرق الشحن المتوفرة:*", user_id, call.message.message_id, reply_markup=kb)

    elif call.data == "pay_binance":
        msg = ("🟡 *Binance Pay (شحن يدوي)*\n\n"
               "1️⃣ قم بتحويل المبلغ (1$ = 100 نقطة) إلى ID باينانس:\n"
               "🆔 *Binance ID:* `549686235` \n\n"
               "2️⃣ بعد التحويل، اضغط على الزر أدناه لإرسال صورة الإيصال للمدير ليقوم بتفعيل نقاطك فوراً.\n\n"
               "⚠️ *ملاحظة:* لا يتم كشف معرف المدير إلا عند إرسال الإثبات.")
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("📸 إرسال صورة الإيصال للتحقق", url=f"tg://user?id={ADMIN_ID}"))
        kb.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="buy_points_main"))
        bot.edit_message_text(msg, user_id, call.message.message_id, reply_markup=kb)

    # --- إكمال باقي الوظائف (كما هي دون تغيير) ---
    elif call.data == "usdt_list":
        kb = types.InlineKeyboardMarkup(row_width=2)
        prices = ["1", "2", "3", "5", "10"]
        buttons = [types.InlineKeyboardButton(f"💵 {p}$", callback_data=f"cpay_{p}") for p in prices]
        kb.add(*buttons)
        kb.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="buy_points_main"))
        bot.edit_message_text("💵 *اختر مبلغ الشحن بـ USDT:*", user_id, call.message.message_id, reply_markup=kb)

    elif call.data.startswith("cpay_"):
        usd = call.data.split("_")[1]
        try:
            res = requests.post("https://pay.crypt.bot/api/createInvoice", headers={"Crypto-Pay-API-Token": CRYPTO_TOKEN}, data={"asset":"USDT","amount":usd}).json()
            pay_url = res['result']['pay_url']
            inv_id = res['result']['invoice_id']
            pts = int(usd) * 100
            kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("💳 رابط الدفع", url=pay_url))
            kb.add(types.InlineKeyboardButton("✅ تأكيد الدفع", callback_data=f"vcheck_{inv_id}_{pts}"))
            bot.send_message(user_id, f"⚠️ *مبلغ الشحن: {usd}$*\nقم بالدفع ثم اضغط تأكيد:", reply_markup=kb)
        except: bot.answer_callback_query(call.id, "❌ خطأ في بوابة CryptoBot")

    elif call.data.startswith("vcheck_"):
        _, inv_id, pts = call.data.split("_")
        res = requests.get(f"https://pay.crypt.bot/api/getInvoices", headers={"Crypto-Pay-API-Token": CRYPTO_TOKEN}, params={"invoice_ids":inv_id}).json()
        if res['result']['items'][0]['status'] == 'paid':
            add_points(user_id, int(pts))
            bot.send_message(user_id, f"✅ *تم استلام {pts} نقطة بنجاح!*")
        else: bot.answer_callback_query(call.id, "❌ لم يتم الدفع بعد.", show_alert=True)

    elif call.data == "stars_list":
        kb = types.InlineKeyboardMarkup(row_width=2)
        opts = {"50": "100", "100": "200", "200": "400", "300": "600", "1000": "2000"}
        buttons = [types.InlineKeyboardButton(f"⭐ {k} ({v}ن)", callback_data=f"pstar_{k}_{v}") for k,v in opts.items()]
        kb.add(*buttons)
        kb.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="buy_points_main"))
        bot.edit_message_text("⭐ *اختر كمية النجوم للشحن:*", user_id, call.message.message_id, reply_markup=kb)

    elif call.data.startswith("pstar_"):
        _, s_amt, p_amt = call.data.split("_")
        bot.send_invoice(user_id, f"شحن {p_amt} نقطة", f"رصيد {p_amt} نقطة بنجوم تيليجرام", f"pts_{p_amt}", "", "XTR", [types.LabeledPrice(f"{p_amt} نقطة", int(s_amt))])

    elif call.data == "view_series":
        kb = types.InlineKeyboardMarkup(row_width=1)
        for s in SERIES_LIST: kb.add(types.InlineKeyboardButton(s, callback_data=f"buy_{s}"))
        kb.add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="main_menu"))
        bot.edit_message_text("📺 *اختر المسلسل لفتحه (100 نقطة):*", user_id, call.message.message_id, reply_markup=kb)

    elif call.data.startswith("buy_"):
        s_name = call.data.replace("buy_", "")
        data = get_user_data(user_id)
        if data and data[0] >= 100:
            add_points(user_id, -100)
            bot.send_message(user_id, f"✅ *تم الفتح!*\n📺 {s_name}\n🔗 {SERIES_LIST[s_name]}")
        else: bot.answer_callback_query(call.id, "⚠️ رصيدك أقل من 100 نقطة!", show_alert=True)

    elif call.data == "my_profile":
        data = get_user_data(user_id)
        msg = (f"👤 *معلومات حسابك:*\n\n🆔 معرفك: `{user_id}`\n💰 رصيدك: `{data[0]}` نقطة\n📅 انضممت في: `{data[2]}`")
        kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="main_menu"))
        bot.edit_message_text(msg, user_id, call.message.message_id, reply_markup=kb)

    elif call.data == "referral_info":
        link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        msg = (f"🎁 *نظام الإحالة*\n\nاحصل على 10 نقاط لكل صديق يشترك عبر الرابط:\n\n{link}")
        kb = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("⬅️ رجوع", callback_data="main_menu"))
        bot.edit_message_text(msg, user_id, call.message.message_id, reply_markup=kb)

    elif call.data == "adm_stats" and user_id == ADMIN_ID:
        total = db_conn.cursor().execute("SELECT COUNT(*) FROM users").fetchone()[0]
        bot.answer_callback_query(call.id, f"📊 عدد المستخدمين: {total}", show_alert=True)

    elif call.data == "adm_broadcast" and user_id == ADMIN_ID:
        m = bot.send_message(ADMIN_ID, "ارسل نص الإذاعة:")
        bot.register_next_step_handler(m, run_bc)

    elif call.data == "adm_add_pts" and user_id == ADMIN_ID:
        m = bot.send_message(ADMIN_ID, "ارسل ID المستخدم:")
        bot.register_next_step_handler(m, get_id_add)

# --- دوال الإدارة ---
def run_bc(message):
    users = db_conn.cursor().execute("SELECT user_id FROM users").fetchall()
    for u in users:
        try: bot.send_message(u[0], message.text)
        except: continue
    bot.send_message(ADMIN_ID, "✅ تمت الإذاعة.")

def get_id_add(message):
    if not message.text.isdigit(): return bot.send_message(ADMIN_ID, "❌ ID خاطئ")
    uid = int(message.text)
    m = bot.send_message(ADMIN_ID, "كم نقطة تود إضافتها؟")
    bot.register_next_step_handler(m, lambda msg: fin_add(msg, uid))

def fin_add(message, uid):
    try:
        amt = int(message.text)
        add_points(uid, amt)
        bot.send_message(ADMIN_ID, f"✅ تم شحن {amt} لـ {uid}")
        try: bot.send_message(uid, f"🎁 تم شحن حسابك بـ {amt} نقطة.")
        except: pass
    except: bot.send_message(ADMIN_ID, "❌ قيمة خاطئة.")

@bot.pre_checkout_query_handler(func=lambda q: True)
def checkout(q): bot.answer_pre_checkout_query(q.id, ok=True)

@bot.message_handler(content_types=['successful_payment'])
def got_pay(m):
    payload = m.successful_payment.invoice_payload
    if payload.startswith("pts_"):
        pts = int(payload.split("_")[1])
        add_points(m.from_user.id, pts)
        bot.send_message(m.chat.id, f"✅ تم شحن {pts} نقطة بنجاح!")

@bot.chat_member_handler()
def kick_reset(u):
    if u.new_chat_member.status in ['left', 'kicked']:
        db_conn.cursor().execute("UPDATE users SET points = 0 WHERE user_id = ?", (u.new_chat_member.user.id,))
        db_conn.commit()

bot.infinity_polling(allowed_updates=['message', 'callback_query', 'chat_member', 'pre_checkout_query'])
