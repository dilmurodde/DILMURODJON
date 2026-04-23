import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters
from yt_dlp import YoutubeDL

# Bot tokeningiz
TOKEN = '8629776604:AAHuCwNwmca0XanHVd9sP0x83j6s0S7nuXg'

async def download(update: Update, context):
    url = update.message.text
    if "instagram.com" not in url: return
    
    msg = await update.message.reply_text("Yuklanmoqda...")
    try:
        with YoutubeDL({'format': 'best', 'outtmpl': 'v.mp4'}) as ydl:
            ydl.download([url])
            btn = InlineKeyboardMarkup([[InlineKeyboardButton("🎵 Musiqa", callback_data=url)]])
            await update.message.reply_video(video=open('v.mp4', 'rb'), reply_markup=btn)
            os.remove('v.mp4')
            await msg.delete()
    except: await update.message.reply_text("Xato!")

async def audio(update: Update, context):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Musiqa tayyorlanmoqda...")
    try:
        opts = {'format': 'bestaudio', 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}], 'outtmpl': 'a'}
        with YoutubeDL(opts) as ydl:
            ydl.download([query.data])
            await context.bot.send_audio(chat_id=query.message.chat_id, audio=open('a.mp3', 'rb'))
            os.remove('a.mp3')
    except: await query.edit_message_text("Xato!")

app = Application.builder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT, download))
app.add_handler(CallbackQueryHandler(audio))
app.run_polling()
