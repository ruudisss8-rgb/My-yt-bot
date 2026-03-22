import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL

TOKEN = '8691187872:AAErOrvL3D_RgQWjLiL8TlaNNFVJrCcBrNs'
bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ආයුබෝවන්! YouTube ලින්ක් එකක් එවන්න, මම ඔබට Quality තෝරාගැනීමට Options ලබා දෙන්නම්. 📥")

@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def handle_link(message):
    url = message.text
    chat_id = message.chat.id
    sent_msg = bot.reply_to(message, "වීඩියෝවේ තොරතුරු පරීක්ෂා කරමින් පවතිනවා... 🔍")

    try:
        with YoutubeDL({'nocheckcertificate': True, 'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get('formats', [])
            
            markup = types.InlineKeyboardMarkup()
            # අපි සාමාන්‍යයෙන් භාවිතා වන quality කිහිපයක් විතරක් තෝරා ගමු
            target_heights = [360, 480, 720]
            added_heights = set()

            for f in formats:
                height = f.get('height')
                if height in target_heights and height not in added_heights:
                    filesize = f.get('filesize') or f.get('filesize_approx')
                    size_str = f"{round(filesize / (1024*1024), 1)}MB" if filesize else "Unknown Size"
                    
                    btn_text = f"🎬 {height}p ({size_str})"
                    callback_data = f"{height}_{url}" # quality සහ url එක callback එකට යවනවා
                    markup.add(types.InlineKeyboardButton(btn_text, callback_data=callback_data))
                    added_heights.add(height)
            
            # Audio Option එකත් අනිවාර්යයෙන්ම දෙමු (ලොකු වීඩියෝ වලට)
            markup.add(types.InlineKeyboardButton("🎧 Audio (MP3)", callback_data=f"audio_{url}"))
            
            bot.edit_message_text("ඔබට අවශ්‍ය Quality එක තෝරන්න:\n(සටහන: 50MB ට වැඩි වීඩියෝ යැවීමට නොහැක)", chat_id, sent_msg.message_id, reply_markup=markup)
            
    except Exception as e:
        bot.edit_message_text(f"දෝෂයක්: {str(e)}", chat_id, sent_msg.message_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    data = call.data.split('_', 1)
    quality = data[0]
    url = data[1]

    bot.delete_message(chat_id, call.message.message_id)
    status_msg = bot.send_message(chat_id, f"ඔබ තේරූ {quality} Quality එක සකසමින් පවතිනවා... ⏳")

    file_name = f'download_{chat_id}.{"mp3" if quality == "audio" else "mp4"}'
    
    if quality == "audio":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': file_name,
            'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '128'}],
        }
    else:
        # තෝරාගත් height එකට ගැලපෙන හොඳම වීඩියෝව සහ ඕඩියෝව එකතු කරනවා
        ydl_opts = {
            'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
            'outtmpl': file_name,
            'merge_output_format': 'mp4',
        }

    try:
        if os.path.exists(file_name): os.remove(file_name)
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open(file_name, 'rb') as f:
            if quality == "audio":
                bot.send_audio(chat_id, f)
            else:
                bot.send_video(chat_id, f)
        
        bot.delete_message(chat_id, status_msg.message_id)
        os.remove(file_name)
    except Exception as e:
        bot.edit_message_text(f"දෝෂයක්: 50MB සීමාව හෝ සර්වර් ගැටලුවක්. {str(e)}", chat_id, status_msg.message_id)

bot.polling()
