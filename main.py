import os
import telebot
from telebot import types
from yt_dlp import YoutubeDL

TOKEN = '8691187872:AAErOrvL3D_RgQWjLiL8TlaNNFVJrCcBrNs'
bot = telebot.TeleBot(TOKEN)

user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ආයුබෝවන්! YouTube ලින්ක් එකක් එවන්න. 📥")

@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def handle_link(message):
    url = message.text
    user_data[message.chat.id] = url
    
    markup = types.InlineKeyboardMarkup()
    btn_video = types.InlineKeyboardButton("🎬 Video (Low Quality)", callback_data="video")
    btn_audio = types.InlineKeyboardButton("🎧 Audio (MP3)", callback_data="audio")
    markup.add(btn_video, btn_audio)
    
    bot.reply_to(message, "ඔයාට අවශ්‍ය කුමන ආකාරයෙන්ද?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    url = user_data.get(chat_id)
    
    if not url:
        bot.answer_callback_query(call.id, "Error: Link එක සොයාගත නොහැක.")
        return

    bot.delete_message(chat_id, call.message.message_id)
    sent_msg = bot.send_message(chat_id, "සකසමින් පවතිනවා... කරුණාකර රැඳී සිටින්න. ⏳")

    if call.data == "video":
        file_name = 'video.mp4'
        ydl_opts = {'format': 'worst', 'outtmpl': file_name, 'nocheckcertificate': True}
    else:
        file_name = 'audio.mp3'
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': file_name,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '128',
            }],
            'nocheckcertificate': True
        }

    try:
        if os.path.exists(file_name): os.remove(file_name)
        
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        
        with open(file_name, 'rb') as f:
            if call.data == "video":
                bot.send_video(chat_id, f)
            else:
                bot.send_audio(chat_id, f)
        
        bot.delete_message(chat_id, sent_msg.message_id)
        os.remove(file_name)
    except Exception as e:
        bot.edit_message_text(f"දෝෂයක්: 50MB සීමාව ඉක්මවා ඇත හෝ {str(e)}", chat_id, sent_msg.message_id)

bot.polling()
