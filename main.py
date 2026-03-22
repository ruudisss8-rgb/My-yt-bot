import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL

# ඔබේ Bot Token එක මෙතනට දාන්න
TOKEN = '8691187872:AAErOrvL3D_RgQWjLiL8TlaNNFVJrCcBrNs'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ආයුබෝවන්! YouTube ලින්ක් එකක් එවන්න. මම එය ඔබට අවශ්‍ය Quality එකෙන් ලබා දෙන්නම්. 📥")

@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def handle_link(message):
    url = message.text
    chat_id = message.chat.id
    sent_msg = bot.reply_to(message, "වීඩියෝවේ තොරතුරු පරීක්ෂා කරමින් පවතිනවා... 🔍")

    # YouTube එකට සාමාන්‍ය Browser එකක් ලෙස පෙනී සිටීමට Headers එකතු කිරීම
    ydl_opts_info = {
        'nocheckcertificate': True,
        'quiet': True,
        'no_warnings': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        with YoutubeDL(ydl_opts_info) as ydl:
            info = ydl.extract_info(url, download=False)
            
            markup = types.InlineKeyboardMarkup()
            # සාමාන්‍යයෙන් පවතින quality options
            target_heights = [360, 480, 720]
            
            for h in target_heights:
                # 50MB සීමාව ගැන පරිශීලකයා දැනුවත් කිරීම වැදගත්
                markup.add(types.InlineKeyboardButton(f"🎬 Video {h}p", callback_data=f"{h}_{url}"))
            
            markup.add(types.InlineKeyboardButton("🎧 Audio (MP3)", callback_data=f"audio_{url}"))
            
            bot.edit_message_text("ඔබට අවශ්‍ය Quality එක තෝරන්න:\n(සටහන: 50MB ට වැඩි වීඩියෝ ටෙලිග්‍රෑම් හරහා යැවිය නොහැක)", chat_id, sent_msg.message_id, reply_markup=markup)
            
    except Exception as e:
        # YouTube Bot Block එකක් තිබේ නම් එය මෙතැනදී හඳුනාගත හැක
        bot.edit_message_text(f"දෝෂයක්: YouTube සීමාවන් නිසා තොරතුරු ගත නොහැක. පසුව උත්සාහ කරන්න. \n\nවිස්තරය: {str(e)}", chat_id, sent_msg.message_id)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    data = call.data.split('_', 1)
    quality = data[0]
    url = data[1]

    bot.delete_message(chat_id, call.message.message_id)
    status_msg = bot.send_message(chat_id, f"වීඩියෝව සකසමින් පවතිනවා... කරුණාකර රැඳී සිටින්න. ⏳")

    file_name = f'video_{chat_id}.{"mp3" if quality == "audio" else "mp4"}'
    
    # ඩවුන්ලෝඩ් කිරීමේදී භාවිතා වන Settings
    ydl_opts = {
        'outtmpl': file_name,
        'nocheckcertificate': True,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    if quality == "audio":
        ydl_opts['format'] = 'bestaudio/best'
    else:
        # ffmpeg නැති වුවහොත් ගැටලුව මගහරවා ගැනීමට 'best' format එක භාවිතා කිරීම
        ydl_opts['format'] = f'best[height<={quality}][ext=mp4]/best[ext=mp4]/best'

    try:
        if os.path.exists(file_name): os.remove(file_name)
        
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        # ගොනුව පවතින්නේ දැයි පරීක්ෂා කර යැවීම
        if os.path.exists(file_name):
            with open(file_name, 'rb') as f:
                if quality == "audio":
                    bot.send_audio(chat_id, f)
                else:
                    bot.send_video(chat_id, f)
            os.remove(file_name)
        else:
            raise FileNotFoundError("Download failed")

        bot.delete_message(chat_id, status_msg.message_id)
        
    except Exception as e:
        # ටෙලිග්‍රෑම් 50MB සීමාව හෝ සර්වර් ගැටලු මෙහිදී පෙන්වයි
        bot.edit_message_text(f"දෝෂයක් සිදු වුණා: {str(e)}", chat_id, status_msg.message_id)

bot.polling()
