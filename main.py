import os
import json
import random
import requests
import asyncio
import subprocess
import edge_tts
import google.generativeai as genai

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY")

genai.configure(api_key=GEMINI_API_KEY)
VOICE = "fa-IR-DilaraNeural"

def generate_script():
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = """
    تو یک تولیدکننده محتوای وایرال اینستاگرام در حوزه هوش مصنوعی و تکنولوژی هستی.
    یک سناریوی جذاب ۲۰ ثانیه‌ای با قلاب میخکوب‌کننده بنویس.
    خروجی را دقیقاً و فقط با این فرمت JSON برگردان:
    {
      "voiceover": "متن فارسی برای گوینده دختر، حداکثر ۵۰ کلمه بدون ایموجی",
      "search_keyword": "technology",
      "caption": "کپشن اینستاگرام به همراه هشتگ"
    }
    """
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    return json.loads(response.text)

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
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={keyword}&per_page=10"
    res = requests.get(url).json()
    hits = res.get("hits", [])
    if not hits:
        hits = requests.get(f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q=technology&per_page=10").json().get("hits", [])
    video_url = random.choice(hits)["videos"]["large"]["url"]
    with open("bg.mp4", "wb") as f:
        f.write(requests.get(video_url).content)

def render_final_reel():
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
    data = generate_script()
    with open("caption.txt", "w", encoding="utf-8") as f:
        f.write(data["caption"])
    await create_voice_and_subtitles(data["voiceover"])
    download_video(data["search_keyword"])
    render_final_reel()

if __name__ == "__main__":
    asyncio.run(main())
