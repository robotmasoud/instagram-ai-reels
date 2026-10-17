import os
import json
import random
import requests
import asyncio
import subprocess
import edge_tts
from google import genai
from google.genai import types

# ۱. دریافت کلیدهای امنیتی از گاوصندوق گیت‌هاب
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY")

# صدای دختر فارسی‌زبان (بسیار طبیعی)
VOICE = "fa-IR-DilaraNeural"

def generate_script():
    """تولید سناریو و کپشن جذاب با هوش مصنوعی جمینای"""
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = """
    تو یک تولیدکننده محتوای حرفه‌ای و وایرال در اینستاگرام در حوزه «هوش مصنوعی، ترفندهای تکنولوژی و نرم‌افزارهای خفن و کاربردی» هستی.
    یک سناریوی بسیار جذاب برای یک ریلز ۲۰ تا ۳۰ ثانیه‌ای بنویس که از ثانیه اول با یک قلاب (Hook) میخکوب‌کننده شروع شود.
    لحن متن باید کاملاً محاوره‌ای، پرانرژی، روان و مناسب خوانش توسط یک دختر جوان باشد.
    
    خروجی را دقیقاً و فقط با این فرمت JSON برگردان:
    {
      "voiceover": "متن فارسی که گوینده باید بخواند (حداکثر ۶۰ تا ۷۰ کلمه، بدون ایموجی و علائم اضافی)",
      "search_keyword": "یک کلمه کلیدی دو کلمه‌ای انگلیسی برای جستجوی ویدیو پس‌زمینه مثل: futuristic technology یا artificial intelligence یا coding screen یا cyber security",
      "caption": "کپشن کامل و حرفه‌ای اینستاگرام به همراه دعوت به تعامل (CTA) و ۵ هشتگ پربازدید مرتبط"
    }
    """
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
        ),
    )
    return json.loads(response.text)

async def create_voice_and_subtitles(text):
    """تولید صدای دختر فارسی و ساخت زیرنویس هماهنگ"""
    communicate = edge_tts.Communicate(text, VOICE, rate="+5%")
    submaker = edge_tts.SubMaker()
    with open("voice.mp3", "wb") as file:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                file.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                submaker.feed(chunk)
    
    with open("subs.vtt", "w", encoding="utf-8") as file:
        file.write(submaker.generate_subs())

def download_video(keyword):
    """دانلود ویدیوی باکیفیت از Pixabay"""
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={requests.utils.quote(keyword)}&video_type=film&per_page=15"
    res = requests.get(url).json()
    hits = res.get("hits", [])
    
    if not hits:
        url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q=technology&per_page=15"
        hits = requests.get(url).json().get("hits", [])
        
    video_data = random.choice(hits)
    video_url = video_data["videos"]["large"]["url"]
    if not video_url:
        video_url = video_data["videos"]["medium"]["url"]
        
    with open("bg.mp4", "wb") as f:
        f.write(requests.get(video_url).content)

def render_final_reel():
    """ترکیب ویدیو، صدای گوینده و زیرنویس فارسی در ابعاد استاندارد ریلز"""
    # تبدیل فرمت زیرنویس و تنظیم استایل وسط صفحه
    subprocess.run(["ffmpeg", "-y", "-i", "subs.vtt", "subs.srt"], check=True)
    
     vf_filter = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "subtitles=subs.srt:force_style='FontName=Vazirmatn,FontSize=18,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2,Shadow=1,Alignment=2,MarginV=70'"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", "bg.mp4",
        "-i", "voice.mp3",
        "-vf", vf_filter,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "192k",
        "-map", "0:v:0", "-map", "1:a:0",
        "-shortest",
        "final_reel.mp4"
    ]
    subprocess.run(cmd, check=True)

async def main():
    print("در حال نوشتن سناریو با Gemini...")
    data = generate_script()
    
    with open("caption.txt", "w", encoding="utf-8") as f:
        f.write(data["caption"])
        
    print("در حال ساخت صدای گوینده (دلارا) و زیرنویس...")
    await create_voice_and_subtitles(data["voiceover"])
    
    print("در حال دانلود ویدیوی پس‌زمینه...")
    download_video(data["search_keyword"])
    
    print("در حال رندر نهایی ویدیوی ریلز...")
    render_final_reel()
    print("ریلز با موفقیت ساخته شد!")

if __name__ == "__main__":
    asyncio.run(main())
