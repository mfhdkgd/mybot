from telegram import Update, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
TOKEN = "token"

warnings = {}
welcome_message = "سلام! خوش اومدی به گروه 🎉"

# تابع برای بررسی اینکه آیا کاربر ادمین است یا نه
async def is_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat.id
    user_id = update.message.from_user.id
    
    admins = [admin.user.id for admin in await update.message.chat.get_administrators()]
    
    return user_id in admins

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من یه ربات پیشرفته‌ی مدیریت گروه هستم 😎")

async def welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for member in update.message.new_chat_members:
        await update.message.reply_text(f"{welcome_message}\n{name_with_mention(member)}")

async def clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این دستور را اجرا کنند.")
        return

    if update.message.reply_to_message:
        try:
            await update.message.reply_to_message.delete()
            await update.message.delete()  # حذف دستور خود ادمین
        except Exception as e:
            await update.message.reply_text("❌ خطا در حذف پیام.")
    else:
        await update.message.reply_text("برای استفاده از /clean باید روی یه پیام ریپلای کنی.")

# ban user 
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌تونن کاربران رو بن کنن.")
        return

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        try:
            await update.message.chat.ban_member(user_id)
            await update.message.reply_text("⛔️ کاربر با موفقیت بن شد.")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در بن کردن کاربر: {e}")
    else:
        await update.message.reply_text("برای بن کردن باید روی پیام کاربر ریپلای کنی.")
#/unban 
async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌تونن کاربر رو از بن دربیارن.")
        return

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        try:
            await update.message.chat.unban_member(user_id)
            await update.message.reply_text("✅ کاربر با موفقیت از بن خارج شد.")
        except Exception as e:
            await update.message.reply_text(f"❌ خطا در آزاد کردن کاربر از بن: {e}")
    else:
        await update.message.reply_text("برای آنبن باید روی پیام کاربر ریپلای کنی.")



async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این دستور را اجرا کنند.")
        return

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id

        try:
            await update.message.chat.restrict_member(
                user_id,
                permissions=ChatPermissions(can_send_messages=False)
            )
            await update.message.reply_text("🔇 کاربر با موفقیت سایلنت شد.")
        except Exception as e:
            await update.message.reply_text("❌ خطا در سایلنت کردن کاربر.")
    else:
        await update.message.reply_text("باید روی پیام کاربر ریپلای کنی تا سایلنت بشه.")

# تابع ضد لینک
async def anti_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # اگر پیام حاوی لینک باشد، آن را پاک می‌کنیم
    if "http://" in update.message.text or "https://" in update.message.text:
        await update.message.delete()

# تابع آزاد کردن (unmute) کاربر
async def unrestrict_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این دستور را اجرا کنند.")
        return

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id

        try:
            await update.message.chat.restrict_member(
                user_id,
                permissions=ChatPermissions(  # همه اجازه‌ها آزاد می‌شن
                    can_send_messages=True,
                    can_send_media_messages=True,
                    can_send_other_messages=True,
                    can_add_web_page_previews=True
                )
            )
            await update.message.reply_text("✅ کاربر آزاد شد و می‌تونه پیام بده.")
        except Exception as e:
            await update.message.reply_text("❌ خطا در آزادسازی کاربر.")
    else:
        await update.message.reply_text("باید روی پیام کاربر ریپلای کنی تا آزاد بشه.")

async def warn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها می‌توانند این دستور را اجرا کنند.")
        return

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
        warnings[user_id] = warnings.get(user_id, 0) + 1

        count = warnings[user_id]
        await update.message.reply_text(f"⚠️ اخطار شماره {count} برای کاربر.")

        if count >= 3:
            await update.message.chat.ban_member(user_id)
            await update.message.reply_text("⛔️ کاربر بعد از 3 اخطار، بن شد.")
            warnings[user_id] = 0

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin(update, context):
        await update.message.reply_text("⛔ فقط ادمین‌ها به پنل دسترسی دارن.")
        return

    keyboard = [
        [InlineKeyboardButton("📢 تنظیم پیام خوش‌آمد", callback_data="set_welcome")],
        [InlineKeyboardButton("🚫 لیست اخطارها", callback_data="show_warnings")],
    ]
    await update.message.reply_text("🎛 پنل مدیریت:", reply_markup=InlineKeyboardMarkup(keyboard))

# هندلر برای دکمه‌ها
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "set_welcome":
        await query.edit_message_text("پیام جدید رو بفرست (حداکثر 200 کاراکتر)")
        context.user_data["awaiting_welcome"] = True

    elif query.data == "show_warnings":
        if not warnings:
            await query.edit_message_text("هنوز هیچ اخطاری ثبت نشده.")
        else:
            msg = "\n".join([f"👤 {uid} - {count} اخطار" for uid, count in warnings.items()])
            await query.edit_message_text(f"📋 لیست اخطارها:\n{msg}")

# دریافت پیام جدید برای تنظیم welcome
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global welcome_message
    if context.user_data.get("awaiting_welcome"):
        welcome_message = update.message.text[:200]
        await update.message.reply_text("✅ پیام خوش‌آمد جدید ذخیره شد.")
        context.user_data["awaiting_welcome"] = False
        return

def name_with_mention(user):
    return f"[{user.full_name}](tg://user?id={user.id})"

# 🎯 اجرای ربات
app = ApplicationBuilder().token(TOKEN).build()

# افزودن هندلرهای دستورات
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("warn", warn))
app.add_handler(CommandHandler("panel", panel))
app.add_handler(CommandHandler("unmute", unrestrict_user))  # اضافه کردن هندلر unmute
app.add_handler(CommandHandler("clean", clean))
app.add_handler(CommandHandler("mute", mute))
app.add_handler(CommandHandler("ban", ban_user))  # اضافه کردن هندلر /ban
app.add_handler(CommandHandler("unban", unban_user))  # اضافه کردن هندلر /unban
app.add_handler(CallbackQueryHandler(button_handler))  # افزودن هندلر برای دکمه‌ها
app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, welcome))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, anti_link))  # افزودن anti_link
app.add_handler(MessageHandler(filters.TEXT, text_handler))

print("🤖 ربات مدیریت پیشرفته آماده‌ست...")
app.run_polling()
