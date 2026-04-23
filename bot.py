import os
import logging
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from yt_dlp import YoutubeDL

# Render uchun veb-server (bot o'chib qolmasligi uchun)
app = Flask('')
@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    # Render avtomatik ravishda PORT o'zgaruvchisini beradi
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

# Logging sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# DIQQAT: Tokenni aynan mana shunday qo'shtirnoq ichida yozing!
TELEGRAM_BOT_TOKEN = '8629776604:AAHuCwNwmca0XanHVd9sP0x83j6s0S7nuXg'

async def start(update: Update, context) -> None:
    await update.message.reply_text("Salom! Instagram havolasini yuboring, men uni yuklab beraman.")

async def download_media(update: Update, context) -> None:
    url = update.message.text
    if "instagram.com" not in url and "instagr.am" not in url:
        await update.message.reply_text("Iltimos, faqat Instagram havolasini yuboring!")
        return
    
    msg = await update.message.reply_text("Yuklanmoqda... Iltimos kuting.")
    try:
        # Yuklab olish sozlamalari
        ydl_opts = {
            'format': 'best',
            'outtmpl': 'downloads/%(id)s.%(ext)s',
            'noplaylist': True,
            'quiet': True
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # Video ostiga musiqa tugmasini qo'shish
            keyboard = [[InlineKeyboardButton("🎵 Musiqani yuklab olish", callback_data=f"audio_{url}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_video(video=open(file_path, 'rb'), reply_markup=reply_markup)
            
            # Faylni o'chirish (joy tejash uchun)
            if os.path.exists(file_path):
                os.remove(file_path)
            await msg.delete()
            
    except Exception as e:
        logger.error(f"Xatolik: {e}")
        await update.message.reply_text(f"Yuklab olishda xatolik yuz berdi. Havolani tekshiring.")

async def audio_callback(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()
    url = query.data.replace("audio_", "")
    
    await query.edit_message_text("Musiqa ajratib olinmoqda...")
    try:
        opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(id)s.%(ext)s',
        }
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Fayl nomini .mp3 ga o'zgartirish
            base_path = ydl.prepare_filename(info).rsplit('.', 1)[0]
            path = base_path + ".mp3"
            
            await context.bot.send_audio(chat_id=query.message.chat_id, audio=open(path, 'rb'))
            if os.path.exists(path):
                os.remove(path)
            await query.edit_message_text("Musiqa muvaffaqiyatli yuborildi!")
    except Exception as e:
        await query.edit_message_text(f"Musiqa yuklashda xato: {e}")

if __name__ == '__main__':
    # Flaskni alohida oqimda ishga tushirish (Render uchun)
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Botni ishga tushirish
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    application.add_handler(CallbackQueryHandler(audio_callback))
    
    print("Bot ishga tushdi...")
    application.run_polling()
    
