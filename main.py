import os
import yt_dlp
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# මෙතනට BotFather දුන්න Token එක දාන්න
TOKEN = '8691187872:AAErOrvL3D_RgQWjLiL8TlaNNFVJrCcBrNs'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ආයුබෝවන්! මට YouTube වීඩියෝ ලින්ක් එකක් එවන්න. මම ඒක ඔයාට එවන්නම්.")

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if "youtube.com" not in url and "youtu.be" not in url:
        await update.message.reply_text("කරුණාකර නිවැරදි YouTube ලින්ක් එකක් එවන්න.")
        return

    sent_message = await update.message.reply_text("වීඩියෝ එක සකසමින් පවතිනවා... කරුණාකර රැඳී සිටින්න්න. ⏳")
    
    file_name = f"{update.message.chat_id}.mp4"
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': file_name,
        'quiet': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        await update.message.reply_video(video=open(file_name, 'rb'), caption="මෙන්න ඔයාගේ වීඩියෝ එක! ✅")
        await sent_message.delete()
    except Exception as e:
        await update.message.reply_text(f"දෝෂයක් සිදු වුණා: {e}")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), download_video))
    print("බොට් වැඩ කරන්න පටන් ගත්තා...")
    app.run_polling()

