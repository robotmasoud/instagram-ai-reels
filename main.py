import os
import json
import random
import re
import requests
import subprocess

PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY")
VOICE = "fa-IR-DilaraNeural"

# بانک سناریوهای ۱۰۰٪ طبیعی، تست‌شده و وایرال اینستاگرام
VIRAL_SCRIPTS = [
    {
        "voiceover": "سه تا سایت هوش مصنوعی مخفی که حس می‌کنی استفاده ازشون غیرقانونیه! اولی سایت لومالبه که هر متنی بهش بدی برات یه ویدیوی سینمایی واقعی می‌سازه. دومی سایت سونو هست که باهاش می‌تونی در ده ثانیه با صدای خودت آهنگ حرفه‌ای بسازی. همین الان این ویدیو رو سیو کن تا گمشون نکنی!",
        "search_keyword": "hacker typing",
        "caption": "سایت‌های مخفی هوش مصنوعی که زندگیت رو عوض می‌کنن! 🤯🔥\n.\nکدوم یکی از این سایت‌ها براتون جالب‌تر بود؟ توی کامنت‌ها بنویسید!\n.\n#هوش_مصنوعی #سایت_کاربردی #تکنولوژی #ترفند_موبایل #ادیت_ویدیو"
    },
    {
        "voiceover": "دیگه هیچ‌وقت برای پاورپوینت و پروژه‌های دانشگاهیت وقت نذار! فقط کافیه وارد سایت گاما اپ بشی و موضوعت رو به فارسی بنویسی. هوش مصنوعی در کمتر از سی ثانیه برات یه فایل ارائه فوق‌العاده حرفه‌ای با عکس و نمودار می‌سازه. حتماً این پست رو برای دوستات بفرست!",
        "search_keyword": "laptop dark",
        "caption": "ساخت پاورپوینت در ۳۰ ثانیه با هوش مصنوعی! 🚀💻\n.\nاسم سایت: Gamma.app\nلایک و سیو یادت نره تا موقع نیاز پیداش کنی!\n.\n#پاورپوینت #دانشجویی #هوش_مصنوعی #ترفند_کامپیوتر #آموزش_رایگان"
    },
    {
        "voiceover": "اگه کیفیت عکس‌هات پایینه یا تار افتاده، اصلاً پاکشون نکن! برو توی سایت آپ‌اسکیل مدیا و عکست رو آپلود کن. این هوش مصنوعی رایگان، کیفیت عکست رو تا چهار برابر بدون هیچ افت کیفیتی بالا می‌بره و کاملاً شفافش می‌کنه. پیجمون رو فالو کن تا هر روز ترفندهای خفن یاد بگیری!",
        "search_keyword": "smartphone screen",
        "caption": "افزایش کیفیت عکس‌های تار با هوش مصنوعی رایگان! 📸✨\n.\nاسم سایت: Upscale.media\nبفرست برای کسی که همیشه عکس‌هاش تار میفته!\n.\n#ادیت_عکس #کیفیت_عکس #هوش_مصنوعی #فتوشاپ #ترفند_اینستاگرام"
    },
    {
        "voiceover": "چطوری صدای هر کسی رو که می‌خوایم با هوش مصنوعی شبیه‌سازی کنیم؟ سایت الون لبز الان قوی‌ترین ابزار صداگذاری دنیاست. فقط کافیه یه فایل صوتی کوتاه بهش بدی تا هر متنی رو که بنویسی، با همون صدا و لحن برات بخونه. برای دریافت لینک مستقیمش، کلمه صدا رو کامنت کن!",
        "search_keyword": "audio studio",
        "caption": "تقلید و شبیه‌سازی صدا با هوش مصنوعی! 🎙️🤖\n.\nکلمه «صدا» رو کامنت کن تا لینک سایت رو برات بفرستم.\n.\n#تولید_محتوا #گویندگی #هوش_مصنوعی #یوتیوبر #ریلز_اینستاگرام"
    }
]

def generate_script():
    """انتخاب یا تولید سناریوی ۱۰۰٪ استاندارد و طبیعی"""
    return random.choice(VIRAL_SCRIPTS)

def format_srt_time(ms):
    """تبدیل میلی‌ثانیه به فرمت استاندارد SRT"""
    hours = int(ms // 3600000)
    ms %= 3600000
    minutes = int(ms // 60000)
    ms %= 60000
    seconds = int(ms // 1000)
    milliseconds = int(ms % 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def parse_vtt_time(t_str):
    """تبدیل زمان VTT به میلی‌ثانیه"""
    parts = t_str.strip().replace(',', '.').split(':')
    if len(parts) == 3:
        h, m, s = parts
    else:
        h = 0
        m, s = parts
    return int(float(h) * 3600000 + float(m) * 60000 + float(s) * 1000)

def convert_vtt_to_short_srt(vtt_file, srt_file, max_words=3):
    """تبدیل زیرنویس‌های طولانی به زیرنویس‌های ۲ الی ۳ کلمه‌ای تیک‌تاکی"""
    with open(vtt_file, "r", encoding="utf-8") as f:
        content = f.read()

    blocks = re.split(r'\n\s*\n', content)
    srt_entries = []
    idx = 1

    for block in blocks:
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        if not lines or "-->" not in block:
            continue
        
        time_line = None
        text_lines = []
        for line in lines:
            if "-->" in line:
                time_line = line
            elif not line.startswith("WEBVTT") and not line.isdigit():
                text_lines.append(line)
        
        if not time_line or not text_lines:
            continue

        start_str, end_str = time_line.split("-->")
        start_ms = parse_vtt_time(start_str)
        end_ms = parse_vtt_time(end_str)
        duration = max(end_ms - start_ms, 200)

        full_text = " ".join(text_lines)
        words = full_text.split()
        if not words:
            continue

        chunks = [" ".join(words[i:i + max_words]) for i in range(0, len(words), max_words)]
        chunk_dur = duration / len(chunks)

        for i, chunk in enumerate(chunks):
            c_start = start_ms + i * chunk_dur
            c_end = start_ms + (i + 1) * chunk_dur
            srt_entries.append(f"{idx}\n{format_srt_time(c_start)} --> {format_srt_time(c_end)}\n{chunk}\n")
            idx += 1

    with open(srt_file, "w", encoding="utf-8") as f:
        f.write("\n".join(srt_entries))

def create_voice_and_subtitles(text):
    """تولید صدای پرانرژی و زیرنویس کوتاه"""
    cmd = [
        "edge-tts",
        "--voice", VOICE,
        "--rate=+12%",
        "--pitch=+2Hz",
        "--text", text,
        "--write-media", "voice.mp3",
        "--write-subtitles", "subs.vtt"
    ]
    subprocess.run(cmd, check=True)
    convert_vtt_to_short_srt("subs.vtt", "subs.srt", max_words=3)

def download_video(keyword):
    """دانلود ویدیوی سینمایی و واقعی (حذف انیمیشن‌های بی‌کیفیت)"""
    queries = [keyword, "coding dark", "cyberpunk city", "smartphone neon", "working laptop"]
    for q in queries:
        url = f"https://pixabay.com/api/videos/?key={PIXABAY_API_KEY}&q={requests.utils.quote(q)}&video_type=film&per_page=15"
        res = requests.get(url).json()
        hits = [h for h in res.get("hits", []) if h.get("duration", 0) >= 8]
        if hits:
            video_data = random.choice(hits)
            video_url = video_data["videos"]["large"]["url"] or video_data["videos"]["medium"]["url"]
            with open("bg.mp4", "wb") as f:
                f.write(requests.get(video_url).content)
            return

def render_final_reel():
    """رندر حرفه‌ای با فیلتر سینمایی تیره، موزیک پس‌زمینه ملایم و زیرنویس بدون کادر سیاه"""
    # ساخت یک لایه صدای اتمسفریک ملایم برای پس‌زمینه تا ویدیو خشک نباشد
    bgm_cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", "anoisesrc=color=brown:amplitude=0.015",
        "-f", "lavfi", "-i", "sine=frequency=110:sample_rate=44100",
        "-filter_complex", "[1:a]volume=0.03,tremolo=f=2:d=0.7[s];[0:a][s]amix=inputs=2:duration=shortest,lowpass=f=400",
        "-t", "40", "bgm.mp3"
    ]
    subprocess.run(bgm_cmd, check=True)

    # فیلتر تصویر: کراپ عمودی + تیره‌تر کردن پس‌زمینه برای درخشش متن + زیرنویس زرد با دورخط مشکی بدون کادر
    vf_filter = (
        "scale=1080:1920:force_original_aspect_ratio=increase,"
        "crop=1080:1920,"
        "eq=brightness=-0.22:contrast=1.15:saturation=1.2,"
        "subtitles=subs.srt:force_style='FontName=Vazirmatn,FontSize=22,Bold=1,PrimaryColour=&H0000FFFF,OutlineColour=&H00000000,BorderStyle=1,Outline=3,Shadow=2,Alignment=2,MarginV=140'"
    )
    
    cmd = [
        "ffmpeg", "-y",
        "-stream_loop", "-1", "-i", "bg.mp4",
        "-i", "voice.mp3",
        "-i", "bgm.mp3",
        "-filter_complex", f"[0:v]{vf_filter}[v];[1:a]volume=1.4[v_voice];[2:a]volume=0.35[v_bgm];[v_voice][v_bgm]amix=inputs=2:duration=first[a]",
        "-map", "[v]", "-map", "[a]",
        "-c:v", "libx264", "-preset", "fast", "-crf", "22",
        "-c:a", "aac", "-b:a", "192k",
        "-shortest",
        "final_reel.mp4"
    ]
    subprocess.run(cmd, check=True)

def main():
    print("در حال آماده‌سازی سناریوی وایرال...")
    data = generate_script()
    with open("caption.txt", "w", encoding="utf-8") as f:
        f.write(data["caption"])
    print("در حال ساخت صدای دلارا و زیرنویس کلمه‌ای...")
    create_voice_and_subtitles(data["voiceover"])
    print("در حال دانلود ویدیوی سینمایی...")
    download_video(data["search_keyword"])
    print("در حال رندر نهایی ویدیو...")
    render_final_reel()
    print("ریلز با موفقیت ساخته شد!")

if __name__ == "__main__":
    main()
