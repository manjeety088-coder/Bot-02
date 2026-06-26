import asyncio
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from pyrogram import Client, filters, idle
from pyrogram.errors import FloodWait
import pyromod 
import yt_dlp
import aiohttp
import os
import time
import math
import re
import threading
import subprocess
from flask import Flask

# ==========================================
# 🌐 IN-BUILT KEEP ALIVE SERVER
# ==========================================
app = Flask(__name__)
@app.route('/')
def health_check():
    return "SZX Master Bot is Running 24/7!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

threading.Thread(target=run_web, daemon=True).start()

# ==========================================
# 🛡️ CREDENTIALS & SECURITY
# ==========================================
ADMIN_ID = 6006752854  

API_ID = 30330414
API_HASH = "98bce6547ca105994c198faf3edc3a0e"
BOT_TOKEN = "8649660643:AAHVme45UDmh0_wu-F3FlMWBh_MGQaZLbzw"
SESSION_STRING = "BQHOzi4AqKiHUnR46JCveds8fJSvksE_Nc9oThO5_6MrO4vroKMkUDup1rcpaPf_Cmn9frid7Rz-W_shN2qM_gIdVhkOzfnR0jU3E6o9B0dciIj5uub7Iaq4tmjMe_iH006LeOxYzmeqVCxahlLNL4j01aDQsjX9a_NcxAOUxS_PCbqJTFa2MfWX_v9gD9Yy3b724qK4SuCwOdL8l0eMyu4CvxTq4YgKGvJxxY7drawZidkmqoK7bSrXRH78Jr-BIWD7Ft3ri29A5VubRNOWblgPFAvuAlyk6P16cq05YYUBFDTwxlBU-MhQtRW9zpC4dQ2K8da96HFXvsm8SmYDkV9SxOCa1gAAAAFmB8ZWAA"

user_app = Client("szx_user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING, in_memory=True, no_updates=True)
bot_app = Client("szx_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

cancel_flag = False
is_running = False

# ==========================================
# 📊 HELPERS, METADATA & UTILITIES
# ==========================================
def humanbytes(size):
    if not size: return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = ((str(days) + "d, ") if days else "") + \
          ((str(hours) + "h, ") if hours else "") + \
          ((str(minutes) + "m, ") if minutes else "") + \
          ((str(seconds) + "s, ") if seconds else "")
    return tmp[:-2]

def clean_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def generate_thumbnail(video_path, output_path):
    try:
        subprocess.run(['ffmpeg', '-i', video_path, '-ss', '00:00:02.000', '-vframes', '1', output_path, '-y'], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if os.path.exists(output_path): return output_path
    except: pass
    return None

def get_video_attributes(file_path):
    try:
        res_dur = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path], capture_output=True, text=True)
        duration = int(float(res_dur.stdout.strip()))
        
        res_dim = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', file_path], capture_output=True, text=True)
        width, height = map(int, res_dim.stdout.strip().split('x'))
        return duration, width, height
    except:
        return 0, 0, 0

async def progress_bar(current, total, ud_type, message, start):
    now = time.time()
    if not hasattr(message, 'last_update_time'): message.last_update_time = 0
    
    if now - message.last_update_time > 3 or current == total:
        message.last_update_time = now
        percentage = current * 100 / total if total > 0 else 0
        speed = current / (now - start) if (now - start) > 0 else 0
        time_to_completion = round((total - current) / speed) * 1000 if speed > 0 else 0
        estimated_total_time = TimeFormatter(time_to_completion)
        
        progress_str = "[{0}{1}]".format(
            ''.join(["█" for i in range(math.floor(percentage / 10))]),
            ''.join(["░" for i in range(10 - math.floor(percentage / 10))]))
        
        tmp = f"{ud_type}\n\n{progress_str}\n🚀 **Progress:** {round(percentage, 2)}%\n⚡ **Speed:** {humanbytes(speed)}/s\n⏱ **ETA:** {estimated_total_time}"
        try:
            await message.edit_text(tmp)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass

async def edit_msg_safe(message, text):
    try:
        await message.edit_text(text)
    except FloodWait as e:
        await asyncio.sleep(e.value)
    except Exception:
        pass

# ==========================================
# 🚀 ULTRA-FAST DOWNLOADER (THE BEAST MODE)
# ==========================================
def yt_dlp_hook(d, message, loop_obj):
    if d['status'] == 'downloading':
        p = d.get('_percent_str', '0%')
        s = d.get('_speed_str', '0B/s')
        eta = d.get('_eta_str', '0s')
        text = f"📥 **Downloading Video (ULTRA FAST)...**\n\n🚀 **Progress:** {p}\n⚡ **Speed:** {s}\n⏱ **ETA:** {eta}"
        
        now = time.time()
        if not hasattr(message, 'last_update_time'): message.last_update_time = 0
        if now - message.last_update_time > 3: 
            message.last_update_time = now
            asyncio.run_coroutine_threadsafe(edit_msg_safe(message, text), loop_obj)

def download_video_ytdlp(url, output_path, message, loop_obj, quality_fmt):
    ydl_opts = {
        'format': quality_fmt,
        'outtmpl': output_path,
        'quiet': True,
        'nocheckcertificate': True,
        'hls_prefer_native': True,             # 🔥 ASLI JADOO: Forces parallel chunk downloading for m3u8
        'concurrent_fragment_downloads': 30,   # 🔥 30 connections ek saath!
        'http_chunk_size': 20971520,           # 🔥 20MB chunks
        'retries': 20,
        'fragment_retries': 20,
        'progress_hooks': [lambda d: yt_dlp_hook(d, message, loop_obj)]
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def parse_chat_id(dest_input, current_chat_id):
    dest_input = dest_input.strip()
    if dest_input == "0":
        return current_chat_id
    elif dest_input.startswith("-100") or dest_input.lstrip('-').isdigit():
        return int(dest_input)
    elif dest_input.startswith("@"):
        return dest_input
    elif "t.me/" in dest_input:
        if "/c/" in dest_input:
            match = re.search(r't\.me/c/(\d+)', dest_input)
            return int("-100" + match.group(1)) if match else dest_input
        else:
            username = dest_input.split("/")[-1]
            return "@" + username if not username.startswith("@") else username
    return dest_input

# ==========================================
# 🛑 COMMANDS
# ==========================================
@bot_app.on_message(filters.command("start") & filters.private)
async def start_cmd(client, message):
    if message.from_user.id != ADMIN_ID: return
    await message.reply_text("👋 **Welcome SZX Boss!**\n\nCommands:\n`/task` - Extract from Telegram\n`/txt` - Extract from TXT File\n`/cancel` - Stop current process\n`/log` - Check bot status")

@bot_app.on_message(filters.command("cancel") & filters.private)
async def cancel_cmd(client, message):
    if message.from_user.id != ADMIN_ID: return
    global cancel_flag, is_running
    if is_running:
        cancel_flag = True
        await message.reply_text("🛑 **Cancel Command Accepted!** Process will stop after the current file.")
    else:
        await message.reply_text("⚠️ Koi process nahi chal raha.")

@bot_app.on_message(filters.command("log") & filters.private)
async def log_cmd(client, message):
    if message.from_user.id != ADMIN_ID: return
    status = "🟢 Running Task" if is_running else "🔴 Idle"
    await message.reply_text(f"📝 **System Status:**\n{status}\nCancel Flag: {cancel_flag}")

# ==========================================
# 📄 TXT BATCH EXTRACTOR 
# ==========================================
@bot_app.on_message(filters.command("txt") & filters.private)
async def handle_txt(client, message):
    if message.from_user.id != ADMIN_ID: return
    global is_running, cancel_flag
    if is_running:
        return await message.reply_text("⚠️ Ek task already chal raha hai.")

    dest_ask = await message.chat.ask("📤 **Destination Group ID / Username:**\n*(Yahin bhejna hai toh 0 likhein)*")
    dest_chat = parse_chat_id(dest_ask.text, message.chat.id)
    
    quality_ask = await message.chat.ask("📺 **Video Quality select karein:**\n(Example: 720, 480, 360. Agar Best/Original chahiye toh `0` likhein)")
    q_val = quality_ask.text.strip()
    quality_fmt = 'best' if q_val == "0" else f'bestvideo[height<={q_val}]+bestaudio/best[height<={q_val}]/best'

    file_ask = await message.chat.ask("📄 **Apni .txt file bhejein:**")
    if not file_ask.document: return await message.reply_text("❌ File nahi mili.")

    m = await message.reply_text("🔄 File read kar raha hoon...")
    
    try:
        is_running = True
        cancel_flag = False
            
        file_path = await client.download_media(file_ask.document)
        with open(file_path, 'r', encoding='utf-8') as f: lines = f.readlines()
        os.remove(file_path)

        total_lines = len(lines)
        processed = 0
        
        await m.edit_text(f"🚀 **SZX TXT Task Started!**\nTotal Files: {total_lines}\nQuality: {q_val + 'p' if q_val != '0' else 'Best'}")
        
        for idx, line in enumerate(lines, 1):
            if cancel_flag:
                await message.reply_text("🛑 **Task Stopped by Admin!**")
                break
                
            line = line.strip()
            idx_http = line.rfind("http")
            if idx_http == -1: continue
            
            name_part = line[:idx_http].strip()
            if name_part.endswith(":"): name_part = name_part[:-1].strip()
            url = line[idx_http:].strip()
            
            try:
                clean_name = clean_filename(name_part)
                final_caption = f"**{name_part}**\n\n━━━━━━━━━━━━━━•\n▸ 𝙀𝙭𝙩𝙧𝙖𝙘𝙩𝙚𝙙 𝘽𝙮 - 𝗦𝗭𝗫 🚩"
                
                file_ext = ".mp4" if "m3u8" in url or "mp4" in url else ".pdf"
                target_filename = f"{clean_name} @szxmocks{file_ext}"

                status_msg = await message.reply_text(f"⚙️ **Processing:** {name_part}")

                if file_ext == ".mp4":
                    await asyncio.to_thread(download_video_ytdlp, url.strip(), target_filename, status_msg, loop, quality_fmt)
                    start_time = time.time()
                    
                    thumb_img = f"thumb_{idx}.jpg"
                    generated_thumb = generate_thumbnail(target_filename, thumb_img)
                    vid_duration, vid_width, vid_height = get_video_attributes(target_filename)
                    
                    await bot_app.send_video(
                        dest_chat, 
                        video=target_filename, 
                        caption=final_caption, 
                        thumb=generated_thumb, 
                        duration=vid_duration,
                        width=vid_width,
                        height=vid_height,
                        progress=progress_bar, 
                        progress_args=("📤 **Uploading Video...**", status_msg, start_time)
                    )
                    if generated_thumb: os.remove(generated_thumb)
                else:
                    await status_msg.edit_text("📥 **Downloading PDF...**")
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url.strip()) as response:
                            with open(target_filename, 'wb') as f: f.write(await response.read())
                    start_time = time.time()
                    await bot_app.send_document(dest_chat, document=target_filename, caption=final_caption, progress=progress_bar, progress_args=("📤 **Uploading PDF...**", status_msg, start_time))

                await status_msg.delete()
                if os.path.exists(target_filename): os.remove(target_filename)
                processed += 1
                
            except Exception as e:
                await message.reply_text(f"❌ **Error in {name_part}:** `{e}`")
                
        if not cancel_flag: await message.reply_text(f"🎉 **Batch Complete!** Uploaded: {processed}/{total_lines}")

    except Exception as e:
        await message.reply_text(f"❌ **Main Error:** `{e}`")
    finally:
        is_running = False
        cancel_flag = False

# ==========================================
# 🔄 TELEGRAM EXTRACTOR
# ==========================================
@bot_app.on_message(filters.command("task") & filters.private)
async def create_task(client, message):
    if message.from_user.id != ADMIN_ID: return
    global is_running, cancel_flag
    if is_running:
        return await message.reply_text("⚠️ Ek task already chal raha hai.")

    mode_ask = await message.chat.ask("⚙️ **Kya karna hai?**\n1. Forward\n2. Re-upload")
    mode = "FORWARD" if mode_ask.text == "1" else "REUPLOAD"
    
    sender_ask = await message.chat.ask("📤 **Kis se bhejna hai?**\n1. Bot\n2. User")
    sender_type = "BOT" if sender_ask.text == "1" else "USER"
    
    start_link_ask = await message.chat.ask("📥 **Start Message LINK:**")
    start_link = start_link_ask.text
    
    topic_id = 0
    private_match = re.search(r't\.me/c/(\d+)/(?:(\d+)/)?(\d+)', start_link)
    public_match = re.search(r't\.me/([a-zA-Z0-9_]+)/(?:(\d+)/)?(\d+)', start_link)
    
    if private_match:
        source_chat = int("-100" + private_match.group(1))
        start_id = int(private_match.group(3))
    elif public_match:
        source_chat = public_match.group(1)
        start_id = int(public_match.group(3))
    else:
        return await message.reply_text("❌ Link Invalid!")

    end_link_ask = await message.chat.ask("🔢 **End Message ID/LINK:** (0 for latest)")
    try: end_id = int(end_link_ask.text)
    except: end_id = int(re.search(r'(\d+)$', end_link_ask.text).group(1))

    dest_ask = await message.chat.ask("📤 **Destination Group ID / Username:** (Yahin ke liye 0 likhein)")
    dest_chat = parse_chat_id(dest_ask.text, message.chat.id)

    replace_ask = await message.chat.ask("✏️ **Kya koi word hatana/replace karna hai?**\n(Format: `PuranaWord|NayaWord` ya hatane ke liye sirf `Word|` likhein. Skip karna hai toh `0` likhein)")
    replace_word = ""
    new_word = ""
    if replace_ask.text != "0" and "|" in replace_ask.text:
        replace_word, new_word = replace_ask.text.split("|", 1)

    check_msg = await message.reply_text("🔄 **Scanning Account Memory... isme 10-15 second lag sakte hain...**")
    try:
        async for _ in user_app.get_dialogs(): pass 
    except Exception: pass 
    await check_msg.delete()

    try:
        is_running = True
        cancel_flag = False
        send_client = bot_app if sender_type == "BOT" else user_app

        if end_id == 0:
            async for last_m in user_app.get_chat_history(source_chat, limit=1): end_id = last_m.id
        
        await message.reply_text(f"🚀 **SZX Task Started!** ID: {start_id} to {end_id}")
        
        for current_id in range(start_id, end_id + 1):
            if cancel_flag:
                await message.reply_text("🛑 **Task Cancelled!**")
                break
                
            try:
                msg = await user_app.get_messages(source_chat, current_id)
                if msg is None or msg.empty or msg.service: continue
                
                original_text = msg.text.html if msg.text else (msg.caption.html if msg.caption else "")
                new_text = re.sub(r'https?://\S+|www\.\S+', '', original_text).strip()
                
                if replace_word:
                    new_text = new_text.replace(replace_word, new_word)
                    
                final_caption = f"{new_text}\n\n━━━━━━━━━━━━━━•\n▸ 𝙀𝙭𝙩𝙧𝙖𝙘𝙩𝙚𝙙 𝘽𝙮 - 𝗦𝗭𝗫 🚩"

                if mode == "FORWARD":
                    if msg.media: await msg.copy(dest_chat, caption=final_caption)
                    else: await user_app.send_message(dest_chat, final_caption)
                    
                elif mode == "REUPLOAD" and msg.media:
                    status_msg = await message.reply_text(f"⚙️ **Processing ID:** {current_id}")
                    start_time = time.time()
                    
                    media_obj = msg.video or msg.document or msg.audio
                    orig_filename = getattr(media_obj, "file_name", f"SZX_File_{current_id}.mp4" if msg.video else f"SZX_Doc_{current_id}.pdf")
                    if not orig_filename: orig_filename = f"SZX_File_{current_id}.mp4"
                    
                    if replace_word:
                        orig_filename = orig_filename.replace(replace_word, new_word)
                    
                    download_path = f"downloads/{orig_filename}"
                    
                    file_path = await user_app.download_media(msg, file_name=download_path, progress=progress_bar, progress_args=("📥 **Downloading...**", status_msg, start_time))
                    
                    thumb_path = None
                    if msg.video and msg.video.thumbs:
                        thumb_path = await user_app.download_media(msg.video.thumbs[0].file_id)
                    
                    vid_duration = msg.video.duration if msg.video else 0
                    vid_width = msg.video.width if msg.video else 0
                    vid_height = msg.video.height if msg.video else 0

                    start_time = time.time()
                    if msg.video: 
                        await send_client.send_video(
                            dest_chat, 
                            file_path, 
                            caption=final_caption, 
                            thumb=thumb_path, 
                            duration=vid_duration,
                            width=vid_width,
                            height=vid_height,
                            progress=progress_bar, 
                            progress_args=("📤 **Uploading...**", status_msg, start_time)
                        )
                    elif msg.document: 
                        await send_client.send_document(dest_chat, file_path, caption=final_caption, thumb=thumb_path, progress=progress_bar, progress_args=("📤 **Uploading...**", status_msg, start_time))
                    elif msg.audio:
                        await send_client.send_audio(dest_chat, file_path, caption=final_caption, progress=progress_bar, progress_args=("📤 **Uploading...**", status_msg, start_time))
                    
                    await status_msg.delete()
                    if os.path.exists(file_path): os.remove(file_path)
                    if thumb_path and os.path.exists(thumb_path): os.remove(thumb_path)

                await asyncio.sleep(2)
            except FloodWait as e:
                await message.reply_text(f"⏳ **FloodWait:** Waiting {e.value} seconds...")
                await asyncio.sleep(e.value + 2)
            except Exception as e:
                if "Message handler check failed" not in str(e):
                    await message.reply_text(f"⚠️ **Skip ID {current_id}:** `{e}`")
                
    except Exception as e:
        await message.reply_text(f"❌ **Task Failed:** `{e}`")
    finally:
        is_running = False
        cancel_flag = False

async def main():
    await user_app.start()
    await bot_app.start()
    print("🤖 SZX Master Bot is Live & Active!")
    await bot_app.send_message(ADMIN_ID, "✅ **SZX System Online!** Server successfully deployed.")
    await idle()
    await user_app.stop()
    await bot_app.stop()

if __name__ == "__main__":
    if not os.path.exists("downloads"): os.makedirs("downloads")
    try:
        loop.run_until_complete(main())
    except Exception as e:
        print(f"System Exit: {e}")
