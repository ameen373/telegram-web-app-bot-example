import os
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
# تعديل السطر المسبب للخطأ لضمان التوافق
from telegram.error import Forbidden, TelegramError

# بياناتك
TOKEN = "8530263010:AAFPegc46edPOQZkWZrUHF4vYLzoGQVX4VU"
ADMIN_ID = 549686235
DB_FILE = "users.txt"

def save_user(user_id):
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f: pass
    with open(DB_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(DB_FILE, "a") as f:
            f.write(f"{user_id}\n")

def get_users():
    if not os.path.exists(DB_FILE): return []
    with open(DB_FILE, "r") as f:
        return list(set(f.read().splitlines()))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    save_user(user_id)
    if user_id == ADMIN_ID:
        keyboard = [['نظام الإذاعة 📢', 'إحصائيات البوت 📊']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text("أهلاً يا أمين، البوت جاهز للإذاعة الآن.", reply_markup=reply_markup)
    else:
        await update.message.reply_text("مرحباً بك!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text

    if text == 'إحصائيات البوت 📊' and user_id == ADMIN_ID:
        users = get_users()
        await update.message.reply_text(f"📈 عدد المشتركين: {len(users)}")

    elif text == 'نظام الإذاعة 📢' and user_id == ADMIN_ID:
        await update.message.reply_text("أرسل الآن ما تريد إذاعته:")
        context.user_data['waiting_broadcast'] = True
    
    elif context.user_data.get('waiting_broadcast') and user_id == ADMIN_ID:
        users = get_users()
        success, blocked, failed = 0, 0, 0
        status_msg = await update.message.reply_text(f"🚀 جاري الإرسال لـ {len(users)}...")
        
        for uid in users:
            try:
                await context.bot.copy_message(chat_id=uid, from_chat_id=ADMIN_ID, message_id=update.message.message_id)
                success += 1
                await asyncio.sleep(0.05) 
            except Forbidden:
                blocked += 1
            except Exception:
                failed += 1
        
        await status_msg.edit_text(f"✅ انتهت الإذاعة:\nنجاح: {success}\nحظر: {blocked}\nفشل: {failed}")
        context.user_data['waiting_broadcast'] = False

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.ALL, handle_message))
    print("--- البوت يعمل الآن بدون أخطاء ---")
    app.run_polling()

if __name__ == '__main__':
    main()
