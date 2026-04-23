import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from yt_dlp import YoutubeDL

# Logging sozlamalari
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot tokenini .env fayldan olish
TELEGRAM_BOT_TOKEN = os.getenv('8629776604:AAHuCwNwmcA0XanHVd9sPOx83j6sOS7nuXg')

async def start(update: Update, context) -> None:
    await update.message.reply_html(f"Salom {update.effective_user.mention_html()}!\n\nInstagram havolasini yuboring.")

async def download_instagram_media(update: Update, context) -> None:
    url = update.message.text
    if not ("instagram.com" in url or "instagr.am" in url):
        await update.message.reply_text("Iltimos, faqat Instagram havolasini yuboring.")
        return

    msg = await update.message.reply_text("Yuklab olinmoqda...")

    try:
        ydl_opts = {'format': 'best', 'outtmpl': 'downloads/%(id)s.%(ext)s', 'merge_output_format': 'mp4', 'paths': {'home': './downloads'}}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            
            # Video ostiga musiqa tugmasini qo'shish
            keyboard = [[InlineKeyboardButton("🎵 Musiqani yuklab olish", callback_data=f"audio_{url}")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_video(video=open(file_path, 'rb'), reply_markup=reply_markup)
            os.remove(file_path)
            await msg.delete()
    except Exception as e:
        await update.message.reply_text(f"Xatolik: {e}")

async def button_callback_handler(update: Update, context) -> None:
    query = update.callback_query
    await query.answer()
    if query.data.startswith("audio_"):
        video_url = query.data.replace("audio_", "")
        await query.edit_message_text("Musiqa ajratib olinmoqda...")
        try:
            ydl_opts_audio = {
                'format': 'bestaudio/best',
                'outtmpl': 'downloads/%(id)s.%(ext)s',
                'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                'paths': {'home': './downloads'}
            }
            with YoutubeDL(ydl_opts_audio) as ydl:
                info = ydl.extract_info(video_url, download=True)
                file_path = ydl.prepare_filename(info).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                await context.bot.send_audio(chat_id=query.message.chat_id, audio=open(file_path, 'rb'))
                os.remove(file_path)
                await query.edit_message_text("Musiqa yuborildi!")
        except Exception as e:
            await query.edit_message_text(f"Xatolik: {e}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_instagram_media))
    app.add_handler(CallbackQueryHandler(button_callback_handler))
    app.run_polling()

if __name__ == '__main__':
    main()
          
