import os
import json
import random
import requests
import asyncio
import subprocess
import edge_tts

PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY")
VOICE = "fa-IR-DilaraNeural"

def generate_script():
    prompt = """
    تو یک تولیدکننده محتوای وایرال اینستاگرام در حوزه هوش مصنوعی و تکنولوژی هستی.
    یک سناریوی جذاب ۲۰ ثانیه‌ای با قلاب میخکوب‌کننده بنویس.
    خروجی را دقیقاً و فقط با این فرمت JSON برگردان و هیچ متن اضافی ننویس:
    {
      "voiceover": "متن فارسی کاملاً محاوره‌ای برای گوینده دختر، حداکثر ۴۵ کلمه بدون ایموجی و بدون کلمات انگلیسی",
      "search_keyword": "technology",
      "caption": "کپشن جذاب اینستاگرام به همراه ۵ هشتگ"
    }
    """
    for _ in range(3):
        try:
            response = requests.post(
                "https://text.pollinations.ai/",
                json={
                    "messages": [{"role": "user", "content": prompt}],
                    "model": "openai",
                    "jsonMode": True
                },
                timeout=30
            )
            text = response.text.strip()
            if "{" in text and "}" in text:
                text = text[text.find("{"):text.rfind("}")+1]
            return json.loads(text)
        except Exception as e:
            print("تلاش مجدد...", e)
            
    # متن پشتیبان در صورت شلوغ بودن سرور رایگان
    return {
        "voiceover": "میدونستی با این ابزار هوش مصنوعی جدید میتونی کارهای روزمره‌ات رو ده برابر سریع‌تر انجام بدی و کلی در زمانت صرفه‌جویی کنی؟ همین الان پیجمون رو فالو کن تا لینک مستقیمش رو برات بفرستم!",
        "search_keyword": "futuristic technology",
        "caption": "بهترین ابزار هوش مصنوعی امسال! 🚀\nبرای دریافت لینک، کلمه هوش رو کامنت کن.\n#هوش_مصنوعی #تکنولوژی #ابزار_هوش_مصنوعی #ترفند #اینستاگرام"
    }

async def create_voice_and_subtitles(text):
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
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={requests.utils.quote(keyword)}&per_page=10"
    res = requests.get(url).json()
    hits = res.get("hits", [])
    if not hits:
        hits = requests.get(f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q=technology&per_page=10").json().get("hits", [])
    
    video_data = random.choice(hits)
    video_url = video_data["videos"]["large"]["url"] or video_data["videos"]["medium"]["url"]
    with open("bg.mp4", "wb") as f:
        f.write(requests.get(video_url).content)

def render_final_reel():
    subprocess.run(["ffmpeg", "-y", "-i", "subs.vtt", "subs.srt"], check=True)
    vf_filter = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "subtitles=subs.srt:force_style='FontName=Vazirmatn,FontSize=16,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=3,Outline=2,Shadow=1,Alignment=2,MarginV=70'"
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
    print("در حال آماده‌سازی سناریو...")
    data = generate_script()
    with open("caption.txt", "w", encoding="utf-8") as f:
        f.write(data["caption"])
    print("در حال ساخت صدای دلارا و زیرنویس...")
    await create_voice_and_subtitles(data["voiceover"])
    print("در حال دانلود ویدیو از Pixabay...")
    download_video(data.get("search_keyword", "technology"))
    print("در حال رندر نهایی ویدیو...")
    render_final_reel()
    print("ریلز با موفقیت ساخته شد!")

if __name__ == "__main__":
    asyncio.run(main())
