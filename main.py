import os
import telebot
from yt_dlp import YoutubeDL

# මෙතනට ඔයාගේ Token එක හරියටම දාන්න
TOKEN = '8691187872:AAErOrvL3D_RgQWjLiL8TlaNNFVJrCcBrNs'
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "ආයුබෝවන්! මට YouTube ලින්ක් එකක් එවන්න, මම ඒක ඔයාට Download කරලා එවන්නම්. 📥")

@bot.message_handler(func=lambda message: True)
def download_video(message):
    url = message.text
    if "youtube.com" in url or "youtu.be" in url:
        sent_msg = bot.reply_to(message, "වීඩියෝ එක සකසමින් පවතිනවා... කරුණාකර රැඳී සිටින්න. ⏳")
        
        # වීඩියෝ එක video.mp4 නමින් සේව් කරන්න කියලා මෙතනින් කියනවා
        file_name = 'video.mp4'
        
        ydl_opts = {
            'format': 'best',
            'outtmpl': file_name,
            'nocheckcertificate': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        }

        try:
            # පරණ වීඩියෝ එකක් තිබ්බොත් ඒක මකනවා
            if os.path.exists(file_name):
                os.remove(file_name)
                
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # වීඩියෝ එක යවනවා
            with open(file_name, 'rb') as video:
                bot.send_video(message.chat.id, video)
            
            bot.delete_message(message.chat.id, sent_msg.message_id)
            os.remove(file_name) # යැවුවට පස්සේ මකනවා

        except Exception as e:
            bot.edit_message_text(f"දෝෂයක් සිදු වුණා: {str(e)}", message.chat.id, sent_msg.message_id)
    else:
        bot.reply_to(message, "කරුණාකර නිවැරදි YouTube ලින්ක් එකක් එවන්න. ⚠️")

bot.polling()
