FROM python:3.10-slim

# ffmpeg අනිවාර්යයෙන් install කිරීම
RUN apt-get update && apt-get install -y ffmpeg

WORKDIR /app

# Requirements install කිරීම
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# කෝඩ් එක සර්වර් එකට දැමීම
COPY . .

# Bot run කිරීම
CMD ["python", "main.py"]
