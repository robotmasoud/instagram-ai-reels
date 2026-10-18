import os
import json
import random
import requests
import subprocess

PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY")

TOPICS = [
    {
        "topic": "معرفی سایت Luma Dream Machine برای تبدیل متن به ویدیوهای سینمایی",
        "keyword": "futuristic technology",
        "script": "سه تا سایتِ هوشِ مصنوعیِ مخفی که حس میکنی استفاده ازشون غیرقانونیه! اولی لوما لَبه که هر متنی بدی ویدیوی سینمایی میسازه. دومی سونو هست که تو ده ثانیه برات آهنگ حرفه‌ای تولید میکنه."
    },
    {
        "topic": "معرفی سایت Gamma.app برای ساخت پاورپوینت و پروژه دانشگاهی در سی ثانیه",
        "keyword": "laptop working",
        "script": "دیگه هیچوقت برای پاورپوینت و پروژه‌های دانشگاهیت وقت نذار! کافیه بری تو سایت گاما اَپ و موضوعت رو به فارسی بنویسی تا در کمتر از سی ثانیه برات یه فایل ارائه فوق‌العاده حرفه‌ای بسازه."
    },
    {
        "topic": "معرفی سایت Upscale.media برای افزایش چهار برابری کیفیت عکس‌های تار",
        "keyword": "smartphone screen",
        "script": "اگه کیفیت عکسات پایینه یا تار افتاده اصلا پاکشون نکن! برو تو سایت آپ اِسکیل مدیا و عکست رو آپلود کن تا کیفیتش رو تا چهار برابر بدون افت کیفیت بالا ببره."
    },
    {
        "topic": "معرفی سایت ElevenLabs برای شبیه‌سازی و تقلید صدای هر فرد با هوش مصنوعی",
        "keyword": "sound studio",
        "script": "چطوری صدای هر کسی رو که میخوایم با هوش مصنوعی شبیه‌سازی کنیم؟ سایت الون لبز الان قوی‌ترین ابزار صداگذاری دنیاست که با یه فایل صوتی کوتاه، هر متنی رو با همون صدا میخونه."
    },
    {
        "topic": "معرفی سایت Perplexity AI که جایگزین بسیار هوشمندتر گوگل برای تحقیق است",
        "keyword": "digital hud",
        "script": "دیگه برای تحقیق و سرچ کردن توی گوگل وقتت رو تلف نکن! سایت پرپلکسیتی مثل یه دستیار هوشمند تمام اطلاعات رو برات مستند و دقیق جمع‌آوری میکنه."
    }
]

def generate_content():
    item = random.choice(TOPICS)
    caption = f"{item['topic']} 🚀🔥\n.\nاگه از این آموزش خوشت اومد برای دوستات بفرست!\n.\n#هوش_مصنوعی #سایت_کاربردی #تکنولوژی #ترفند_آموزشی #پیج_لیام"
    return item["script"], item["keyword"], caption

def generate_subtitles_file(text):
    words = text.split()
    chunks = [" ".join(words[i:i + 3]) for i in range(0, len(words), 3)]
    
    chunks.append("اگه به این سری موضوعات علاقه داری،")
    chunks.append("فالو و سیو یادت نره! 🔥")
    chunks.append("پیج لیام 🚀")
    
    total_duration = len(chunks) * 2.2
    
    srt_lines = []
    for i, chunk in enumerate(chunks):
        start_sec = i * 2.2
        end_sec = (i + 1) * 2.2
        
        start_time = f"00:00:{int(start_sec):02d},{int((start_sec % 1) * 1000):03d}"
        end_time = f"00:00:{int(end_sec):02d},{int((end_sec % 1) * 1000):03d}"
        
        srt_lines.append(f"{i+1}\n{start_time} --> {end_time}\n{chunk}\n")
        
    with open("subs.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))
        
    return total_duration

def download_high_quality_video(keyword):
    """دانلود ویدیوی باکیفیت مرتبط با استفاده از کلید معتبر Pixabay"""
    url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={requests.utils.quote(keyword)}&per_page=15"
    res = requests.get(url).json()
    hits = [h for h in res.get("hits", []) if h.get("duration", 0) >= 8]
    
    if not hits:
        url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q=technology&per_page=15"
        res = requests.get(url).json()
        hits = res.get("hits", [])
        
    video_data = random.choice(hits)
    video_url = video_data["videos"]["large"]["url"] or video_data["videos"]["medium"]["url"]
    
    with open("bg.mp4", "wb") as f:
        f.write(requests.get(video_url).content)

def render_silent_reel(duration):
    vf_filter = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "eq=brightness=-0.15:contrast=1.2:saturation=1.25,"
        "subtitles=subs.srt:force_style='FontName=Vazirmatn,FontSize=24,Bold=1,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3.5,Shadow=2,Alignment=2,MarginV=150'"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", "bg.mp4",
        "-vf", vf_filter,
        "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-t", str(duration),
        "final_reel.mp4"
    ]
    subprocess.run(cmd, check=True)

def main():
    print("در حال آماده‌سازی محتوا...")
    script_text, keyword, caption = generate_content()
    
    with open("caption.txt", "w", encoding="utf-8") as f:
        f.write(caption)
        
    print(f"موضوع انتخابی با کلمه کلیدی: {keyword}")
    duration = generate_subtitles_file(script_text)
    
    print("در حال دانلود ویدیوی باکیفیت از Pixabay...")
    download_high_quality_video(keyword)
    
    print("در حال رندر نهایی ویدیوی بی‌صدا...")
    render_silent_reel(duration)
    print("ریلز با موفقیت ساخته شد!")

if __name__ == "__main__":
    main()
