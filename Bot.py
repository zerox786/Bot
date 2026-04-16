from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import uuid
import requests
import asyncio
import os
# ================== CONFIG ==================
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_USERNAME = os.getenv("BOT_USERNAME")
ADMIN_ID = int(os.getenv("ADMIN_ID"))

API_KEY = os.getenv("API_KEY")

CHANNEL_LINK = "https://t.me/xahdgadhghjg"

# 👉 SAME FIXED PHOTO (yaha apni ek permanent photo ka file_id daal)
FIXED_PHOTO = "AgACAgUAAxkBAANCadkvpPz49A0Nt63g7mBa__Vx0iIAAr0Maxs-dtFWtns-23dmfwgBAAMCAAN5AAM7BA"

data_store = {}

# ================== SHORTENER ==================
def shorten_link(url):
    try:
        api_url = f"https://shrinkme.io/api?api={API_KEY}&url={url}"
        res = requests.get(api_url).json()
        return res.get("shortenedUrl", url)
    except:
        return url

# ================== START ==================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args

    if not args:
        await update.message.reply_text("Bot Running ✅")
        return

    key = args[0]

    # 🔓 FINAL UNLOCK
    if key.startswith("unlock_"):
        real_key = key.replace("unlock_", "")

        if real_key in data_store:
            file_link, photo = data_store[real_key]

            msg = await update.message.reply_photo(
                photo=photo,
                caption=f"⚠️ ‼️ Forward the Files to Saved Messages or somewhere else before Downloading it.\nIt will get Delete after 10 minutes.‼️\n📥 Download:\n{file_link}"
            )

            # ⏱️ AUTO DELETE AFTER 10 MIN
            await asyncio.sleep(600)
            await msg.delete()

        else:
            await update.message.reply_text("❌ Link expired")

    # 👀 PREVIEW
    else:
        if key in data_store:

            unlock_link = f"https://t.me/{BOT_USERNAME}?start=unlock_{key}"
            short_link = shorten_link(unlock_link)

            keyboard = [
                [InlineKeyboardButton("📥 Click Here to Download", url=short_link)],
                [InlineKeyboardButton("Tutorial", url=CHANNEL_LINK)]
            ]

            await update.message.reply_photo(
                photo=FIXED_PHOTO,
                caption="<b>Your Link Is Ready 👇 </b>",
                parse_mode="HTML",
                
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

        else:
            await update.message.reply_text("❌ Invalid link")

# ================== ADMIN ==================
async def handle_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_ID:
        return

    if update.message.photo and update.message.caption:
        file_link = update.message.caption.strip()
        photo = update.message.photo[-1].file_id

        key = str(uuid.uuid4())[:8]
        data_store[key] = (file_link, photo)

        bot_link = f"https://t.me/{BOT_USERNAME}?start={key}"

        await update.message.reply_text(f"✅ Ready:\n{bot_link}")

# ================== RUN ==================
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_admin))

import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running")

def run_server():
    server = HTTPServer(("0.0.0.0", 10000), Handler)
    server.serve_forever()

# server background me chalega
threading.Thread(target=run_server).start()

# bot main thread me chalega (IMPORTANT)
try:
    print("Bot Running 🚀")
    app.run_polling()
except Exception as e:
    print("BOT ERROR:", e)
