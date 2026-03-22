import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL

TOKEN = '8691187872:AAErOrvL3D_RgQWjLiL8TlaNNFVJrCcBrNs'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ඔන්න වැඩේ අලුත් කළා! ලින්ක් එකක් එවන්න බලන්න. 📥")

@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def handle_link(message):
    url = message.text
    sent_msg = bot.reply_to(message, "වීඩියෝ තොරතුරු ගනිමින්... 🔍")

    try:
        with YoutubeDL({'nocheckcertificate': True, 'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            markup = types.InlineKeyboardMarkup()
            
            # පවතින quality ටික ලස්සනට පෙන්නන්න මෙහෙම කරමු
            formats = [360, 480, 720]
            for res in formats:
                markup.add(types.InlineKeyboardButton(f"🎬 Video {res}p", callback_data=f"{res}_{url}"))
            
            markup.add(types.InlineKeyboardButton("🎧 Audio (MP3)", callback_data=f"audio_{url}"))
            bot.edit_message_text("ඔබට අවශ්‍ය Quality එක තෝරන්න:", message.chat.id, sent_msg.message_id, reply_markup=markup)
            
    except Exception as e:
        bot.edit_message_text(f"තොරතුරු ගැනීමේ දෝෂයක්: {str(e)}", message.chat.id, sent_msg.message_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    q_data = call.data.split('_', 1)
    quality = q_data[0]
    url = q_data[1]

    bot.delete_message(chat_id, call.message.message_id)
    status_msg = bot.send_message(chat_id, "ඩවුන්ලෝඩ් වෙමින් පවතී... ⏳")

    file_name = f'file_{chat_id}.{"mp3" if quality == "audio" else "mp4"}'
    
    # FFmpeg ප්‍රශ්නය මගහරින්න මේ විදිහට දෙනවා
    if quality == "audio":
        ydl_opts = {'format': 'bestaudio/best', 'outtmpl': file_name, 'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3'}]}
    else:
        # 50MB සීමාව නිසා අපි කෙලින්ම quality එකට limit එකක් දෙනවා
        ydl_opts = {'format': f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 'outtmpl': file_name}

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
        bot.edit_message_text(f"දෝෂයක්: බොහොමයක් විට 50MB ට වැඩියි. {str(e)}", chat_id, status_msg.message_id)

bot.polling()
