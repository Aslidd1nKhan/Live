from pyrogram import Client, filters
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped
import yt_dlp
import os
import json

# Config
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID"))
ADMIN_LIST = "admins.json"

# Init bot
app = Client("voice_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
vc = PyTgCalls(app)

# Load admin list
def load_admins():
    if not os.path.exists(ADMIN_LIST):
        return []
    with open(ADMIN_LIST, "r") as f:
        return json.load(f)

def save_admins(admins):
    with open(ADMIN_LIST, "w") as f:
        json.dump(admins, f)

admins = load_admins()

# Function to get audio URL
def get_audio_url(video_url):
    ydl_opts = {
        'format': 'bestaudio',
        'noplaylist': True,
        'quiet': True,
        'extract_flat': False
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(video_url, download=False)
        return info['url']

# Start command
@app.on_message(filters.command("start"))
def start(client, message):
    message.reply_text("🎵 Bot ishga tushdi! Musiqa tinglash uchun: /play URL\nAdmin qo‘shish: /addadmin @username\nAdminlar: /admins")

# Add admin command
@app.on_message(filters.command("addadmin"))
def add_admin(client, message):
    if message.from_user.username not in admins:
        message.reply_text("❌ Faqat adminlar qo‘sha oladi!")
        return
    
    if len(message.command) < 2:
        message.reply_text("❌ Iltimos, foydalanuvchi @username kiriting!")
        return
    
    new_admin = message.command[1].lstrip("@")
    admins.append(new_admin)
    save_admins(admins)
    message.reply_text(f"✅ @{new_admin} admin sifatida qo‘shildi!")

# Show admins
@app.on_message(filters.command("admins"))
def show_admins(client, message):
    admin_list = "\n".join([f"@{admin}" for admin in admins])
    message.reply_text(f"👑 Adminlar:\n{admin_list}")

# Play command
@app.on_message(filters.command("play"))
def play(client, message):
    if message.from_user.username not in admins:
        message.reply_text("❌ Faqat adminlar musiqani boshlashi mumkin!")
        return
    
    if len(message.command) < 2:
        message.reply_text("❌ Iltimos, YouTube havolasini yuboring!")
        return
    
    video_url = message.command[1]
    audio_url = get_audio_url(video_url)
    vc.join_chat(CHAT_ID)
    vc.play(AudioPiped(audio_url))
    message.reply_text("✅ Musiqa translyatsiya qilinmoqda!")

# Stop command
@app.on_message(filters.command("stop"))
def stop(client, message):
    if message.from_user.username not in admins:
        message.reply_text("❌ Faqat adminlar to‘xtata oladi!")
        return
    
    vc.stop()
    message.reply_text("⏹ Translyatsiya to‘xtatildi.")

# Run bot
if __name__ == "__main__":
    app.start()
    vc.start()
    app.idle()
