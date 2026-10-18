import os
import json
import random
import requests
import subprocess

# استفاده از کلید Pexels (یا اگر ندارید از همان متغیر قبلی استفاده می‌شود)
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY") or os.environ.get("PIXABAY_API_KEY")

TOPICS = [
    {
        "topic": "معرفی سایت Luma Dream Machine برای تبدیل متن به ویدیوهای سینمایی",
        "keyword": "futuristic cinematic technology",
        "script": "سه تا سایتِ هوشِ مصنوعیِ مخفی که حس میکنی استفاده ازشون غیرقانونیه! اولی لوما لَبه که هر متنی بدی ویدیوی سینمایی میسازه. دومی سونو هست که تو ده ثانیه برات آهنگ حرفه‌ای تولید میکنه."
    },
    {
        "topic": "معرفی سایت Gamma.app برای ساخت پاورپوینت و پروژه دانشگاهی در سی ثانیه",
        "keyword": "modern office laptop working",
        "script": "دیگه هیچوقت برای پاورپوینت و پروژه‌های دانشگاهیت وقت نذار! کافیه بری تو سایت گاما اَپ و موضوعت رو به فارسی بنویسی تا در کمتر از سی ثانیه برات یه فایل ارائه فوق‌العاده حرفه‌ای بسازه."
    },
    {
        "topic": "معرفی سایت Upscale.media برای افزایش چهار برابری کیفیت عکس‌های تار",
        "keyword": "smartphone editing screen",
        "script": "اگه کیفیت عکسات پایینه یا تار افتاده اصلا پاکشون نکن! برو تو سایت آپ اِسکیل مدیا و عکست رو آپلود کن تا کیفیتش رو تا چهار برابر بدون افت کیفیت بالا ببره."
    },
    {
        "topic": "معرفی سایت ElevenLabs برای شبیه‌سازی و تقلید صدای هر فرد با هوش مصنوعی",
        "keyword": "voice recording studio microphone",
        "script": "چطوری صدای هر کسی رو که میخوایم با هوش مصنوعی شبیه‌سازی کنیم؟ سایت الون لبز الان قوی‌ترین ابزار صداگذاری دنیاست که با یه فایل صوتی کوتاه، هر متنی رو با همون صدا میخونه."
    },
    {
        "topic": "معرفی سایت Perplexity AI که جایگزین بسیار هوشمندتر گوگل برای تحقیق است",
        "keyword": "cyberpunk digital hud screen",
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
    
    # اضافه شدن نام برند شما و کال‌تواکشن پایانی
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
    """دانلود ویدیوهای بسیار باکیفیت و سینمایی از موتور قدرتمند Pexels"""
    headers = {"Authorization": PEXELS_API_KEY}
    url = f"https://api.pexels.com/videos/search?query={requests.utils.quote(keyword)}&per_page=15&orientation=portrait"
    
    res = requests.get(url, headers=headers).json()
    videos = res.get("videos", [])
    
    if not videos:
        # جستجوی پشتیبان با کلیدواژه عمومی تکنولوژی
        url = f"https://api.pexels.com/videos/search?query=technology&per_page=15&orientation=portrait"
        res = requests.get(url, headers=headers).json()
        videos = res.get("videos", [])
        
    if videos:
        video_obj = random.choice(videos)
        # پیدا کردن بهترین کیفیت ویدیو
        video_files = video_obj.get("video_files", [])
        hd_files = [vf for vf in video_files if vf.get("quality") == "hd" or vf.get("width", 0) >= 1080]
        selected_file = hd_files[0] if hd_files else video_files[0]
        
        video_url = selected_file["link"]
        with open("bg.mp4", "wb") as f:
            f.write(requests.get(video_url).content)
    else:
        raise Exception("ویدیویی از Pexels یافت نشد. لطفاً کلید PEXELS_API_KEY را بررسی کنید.")

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
        
    print(f"موضوع انتخابی با کلمه کلیدی سینمایی: {keyword}")
    duration = generate_subtitles_file(script_text)
    
    print("در حال دانلود ویدیوی باکیفیت مرتبط از Pexels...")
    download_high_quality_video(keyword)
    
    print("در حال رندر نهایی ویدیوی بی‌صدا با کیفیت فوق‌العاده...")
    render_silent_reel(duration)
    print("ریلز با موفقیت ساخته شد!")

if __name__ == "__main__":
    main()
