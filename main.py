import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL

# ඔබේ ටෝකන් එක මෙතනට දාන්න
TOKEN = '8691187872:AAErOrvL3D_RgQWjLiL8TlaNNFVJrCcBrNs'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ආයුබෝවන්! YouTube ලින්ක් එකක් එවන්න. 📥")

@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def handle_link(message):
    url = message.text
    chat_id = message.chat.id
    sent_msg = bot.reply_to(message, "තොරතුරු පරීක්ෂා කරමින්... 🔍")

    try:
        with YoutubeDL({'nocheckcertificate': True, 'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            markup = types.InlineKeyboardMarkup()
            
            # පවතින quality වර්ග සොයා ගැනීම
            available_heights = set(f.get('height') for f in info.get('formats', []) if f.get('height'))
            target_heights = [360, 480, 720]

            for h in target_heights:
                if h in available_heights:
                    markup.add(types.InlineKeyboardButton(f"🎬 Video {h}p", callback_data=f"{h}_{url}"))
            
            markup.add(types.InlineKeyboardButton("🎧 Audio (MP3)", callback_data=f"audio_{url}"))
            bot.edit_message_text("ඔබට අවශ්‍ය Quality එක තෝරන්න:", chat_id, sent_msg.message_id, reply_markup=markup)
            
    except Exception as e:
        bot.edit_message_text(f"දෝෂයක්: {str(e)}", chat_id, sent_msg.message_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    data = call.data.split('_', 1)
    quality = data[0]
    url = data[1]

    bot.delete_message(chat_id, call.message.message_id)
    status_msg = bot.send_message(chat_id, f"සකසමින් පවතිනවා... ⏳")

    file_name = f'dl_{chat_id}.{"mp3" if quality == "audio" else "mp4"}'
    
    if quality == "audio":
        ydl_opts = {'format': 'bestaudio/best', 'outtmpl': file_name, 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '128'}]}
    else:
        ydl_opts = {'format': f'bestvideo[height<={quality}]+bestaudio/best', 'outtmpl': file_name, 'merge_output_format': 'mp4'}

    try:
        if os.path.exists(file_name): os.remove(file_name)
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open(file_name, 'rb') as f:
            if quality == "audio": bot.send_audio(chat_id, f)
            else: bot.send_video(chat_id, f)
        
        bot.delete_message(chat_id, status_msg.message_id)
        os.remove(file_name)
    except Exception as e:
        bot.edit_message_text(f"දෝෂයක්: 50MB සීමාව හෝ FFmpeg ගැටලුවක්. {str(e)}", chat_id, status_msg.message_id)

bot.polling()
