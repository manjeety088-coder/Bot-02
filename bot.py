
import nest_asyncio
nest_asyncio.apply()

from pyrogram import Client, filters
import pyromod 
from pyrogram.errors import FloodWait
import asyncio
import re
import os
import time

# Credentials
API_ID = 30330414
API_HASH = "98bce6547ca105994c198faf3edc3a0e"
BOT_TOKEN = "8700962493:AAFAamtjbUaNm-ibady6_7eyZFEYcHraXmA"

# 👇 YAHAN APNA STRING SESSION PASTE KAREIN 👇
SESSION_STRING = "BQHOzi4AqKiHUnR46JCveds8fJSvksE_Nc9oThO5_6MrO4vroKMkUDup1rcpaPf_Cmn9frid7Rz-W_shN2qM_gIdVhkOzfnR0jU3E6o9B0dciIj5uub7Iaq4tmjMe_iH006LeOxYzmeqVCxahlLNL4j01aDQsjX9a_NcxAOUxS_PCbqJTFa2MfWX_v9gD9Yy3b724qK4SuCwOdL8l0eMyu4CvxTq4YgKGvJxxY7drawZidkmqoK7bSrXRH78Jr-BIWD7Ft3ri29A5VubRNOWblgPFAvuAlyk6P16cq05YYUBFDTwxlBU-MhQtRW9zpC4dQ2K8da96HFXvsm8SmYDkV9SxOCa1gAAAAFmB8ZWAA"

user_app = Client("szx_user", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING, in_memory=True)
bot_app = Client("szx_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)

async def progress_bar(current, total, msg_id, action, start_time):
    elapsed_time = time.time() - start_time
    percentage = (current / total) * 100 if total > 0 else 0
    speed = current / elapsed_time if elapsed_time > 0 else 0
    print(f"⏳ [{action}] Msg {msg_id}: {percentage:.1f}% | Speed: {speed/(1024*1024):.2f} MB/s", end="\r")

@bot_app.on_message(filters.command("start") & filters.private)
async def bot_menu(client, message):
    await message.reply_text("👋 Hello SZX Boss! Main ready hoon. Naya task shuru karne ke liye /task bhejein.")

@bot_app.on_message(filters.command("task") & filters.private)
async def create_task(client, message):
    mode_ask = await message.chat.ask("⚙️ **Kya karna hai?**\n1. Forward (Fast Direct Copy)\n2. Re-upload (Download & Upload)\n\nReply 1 or 2:")
    mode = "FORWARD" if mode_ask.text == "1" else "REUPLOAD"
    
    sender_ask = await message.chat.ask("📤 **Message kis account se bhejna hai?**\n1. Bot Account se\n2. User Account se\n\nReply 1 or 2:")
    sender_type = "BOT" if sender_ask.text == "1" else "USER"
    
    if mode == "FORWARD" and sender_type == "BOT":
        await message.reply_text("⚠️ *Notice: Bot source me nahi hai, isliye FORWARD automatically 'User Account' se hoga.*")
        sender_type = "USER"

    # Start Link
    start_link_ask = await message.chat.ask("📥 **Start Message ka LINK bhejein:**")
    start_link = start_link_ask.text
    
    topic_id = 0
    private_match = re.search(r't\.me/c/(\d+)/(?:(\d+)/)?(\d+)', start_link)
    public_match = re.search(r't\.me/([a-zA-Z0-9_]+)/(?:(\d+)/)?(\d+)', start_link)
    
    if private_match:
        source_chat = int("-100" + private_match.group(1))
        topic_id = int(private_match.group(2)) if private_match.group(2) else 0
        start_id = int(private_match.group(3))
    elif public_match:
        source_chat = public_match.group(1)
        topic_id = int(public_match.group(2)) if public_match.group(2) else 0
        start_id = int(public_match.group(3))
    else:
        await message.reply_text("❌ Link samajh nahi aaya! Task cancel.")
        return

    # End Link
    end_link_ask = await message.chat.ask("🔢 **End Message ka LINK bhejein:**\n*(Ya fir number me ID likh dein)*")
    end_link = end_link_ask.text
    
    end_id = 0
    if end_link != "0":
        end_private = re.search(r't\.me/c/(\d+)/(?:(\d+)/)?(\d+)', end_link)
        end_public = re.search(r't\.me/([a-zA-Z0-9_]+)/(?:(\d+)/)?(\d+)', end_link)
        if end_private: end_id = int(end_private.group(3))
        elif end_public: end_id = int(end_public.group(3))
        else:
            try: end_id = int(end_link)
            except: pass

    # Destination
    dest_ask_type = await message.chat.ask("📤 **Destination kahan set karna hai?**\n1. Kisi Group me\n2. Yahin (Isi Bot ki chat me)\n\nReply 1 or 2:")
    if dest_ask_type.text == "1":
        dest_ask = await message.chat.ask("📤 **Destination Group ID bhejein:**")
        dest_chat = int(dest_ask.text)
    else:
        dest_chat = message.chat.id # Isi chat me bhejega

    # Custom Text Replace
    replace_ask = await message.chat.ask("📝 **Kya koi specific word/text remove ya replace karna hai?**\n*(Haan toh wo text bhejein, nahi toh 0 likhein)*")
    replace_word = replace_ask.text

    new_word = "0"
    if replace_word != "0":
        new_ask = await message.chat.ask(f"🔄 **'{replace_word}' ki jagah kya likhna hai?**\n*(Sirf delete karna hai toh 0 likhein)*")
        new_word = new_ask.text

    m = await message.reply_text("🔄 **Rukiye!** System load ho raha hai...")
    
    try:
        # Cache load karna zaroori hai Peer ID Invalid error se bachne ke liye
        async for dialog in user_app.get_dialogs(limit=300): pass
        await m.edit_text(f"🚀 Process started!\nMode: {mode}\nIDs: {start_id} to {'Last' if end_id == 0 else end_id}\n\nConsole check karein, wahan 'Next -> Next' ho raha hoga!")
        asyncio.create_task(run_szx_process(message, mode, sender_type, source_chat, dest_chat, start_id, end_id, topic_id, replace_word, new_word))
    except Exception as e:
        await m.edit_text(f"❌ Error: {e}")

async def run_szx_process(message, mode, sender_type, source_chat, dest_chat, start_id, end_id, topic_id, replace_word, new_word):
    processed_count = 0
    try:
        if end_id == 0:
            async for last_m in user_app.get_chat_history(source_chat, limit=1):
                end_id = last_m.id

        send_client = bot_app if sender_type == "BOT" else user_app
        print("\n🚀 Next -> Next Process Shuru...\n")
        
        # EXACTLY "NEXT -> NEXT" LOGIC
        for current_id in range(start_id, end_id + 1):
            try:
                print(f"🔍 Reading Link Message ID: {current_id}...", end="\r")
                
                # Ek-ek karke message uthana (taaki koi error miss na ho)
                msg = await user_app.get_messages(source_chat, current_id)
                
                if msg is None or msg.empty or msg.service:
                    print(f"⏭️ Msg {current_id} khali hai ya delete ho gaya hai. Next ->")
                    continue
                    
                msg_topic_id = msg.reply_to_top_message_id or msg.reply_to_message_id
                if topic_id != 0 and msg_topic_id != topic_id:
                    print(f"⏭️ Msg {current_id} is topic ka nahi hai. Next ->")
                    continue
                
                original_text = msg.text.html if msg.text else (msg.caption.html if msg.caption else "")
                new_text = original_text
                
                if original_text:
                    new_text = original_text.replace("Anish", "SZX").replace("𝗔𝗯𝗵𝗶𝘀𝗵𝗲𝗸 𝗦𝗮𝗻𝗷𝗶𝘁 🚩🇮🇳", "SZX").replace("Abhishek Sanjit", "SZX")
                    
                    if replace_word != "0":
                        replacement = "" if new_word == "0" else new_word
                        new_text = new_text.replace(replace_word, replacement)

                    new_text = re.sub(r'<a href="[^"]+">([^<]+)</a>', r'\1', new_text)
                    new_text = re.sub(r'\s*\(?https?://(?:chat\.)?whatsapp\.com/[^\s<]+\)?\s*', ' ', new_text)
                    new_text = re.sub(r'https?://\S+|www\.\S+', '', new_text).strip()
                
                branding_text = "\n\n━━━━━━━━━━━━━━•\n▸ 𝙀𝙭𝙩𝙧𝙖𝙘𝙩𝙚𝙙 𝘽𝙮 - 𝗦𝗭𝗫 🚩"
                final_caption = f"{new_text}{branding_text}" if new_text else branding_text

                if mode == "FORWARD":
                    if new_text:
                        if msg.media:
                            await msg.copy(dest_chat, caption=final_caption)
                        else:
                            await user_app.send_message(dest_chat, new_text)
                    else:
                        await msg.copy(dest_chat)
                    
                    await asyncio.sleep(2)
                    print(f"✅ Msg {current_id} Forward ho gaya! Next ->")
                    processed_count += 1
                    
                elif mode == "REUPLOAD" and msg.media:
                    thumb_path = None
                    media_obj = msg.video or msg.document or msg.audio
                    if media_obj and getattr(media_obj, "thumbs", None):
                        try: thumb_path = await user_app.download_media(media_obj.thumbs[0].file_id)
                        except: pass

                    start_time = time.time()
                    file_path = await user_app.download_media(msg, progress=progress_bar, progress_args=(msg.id, "DL", start_time))
                    
                    print(f"📤 Uploading Msg {current_id}...", end="\r")
                    if msg.video:
                        await send_client.send_video(dest_chat, file_path, caption=final_caption, thumb=thumb_path)
                    elif msg.document:
                        await send_client.send_document(dest_chat, file_path, caption=final_caption, thumb=thumb_path)
                    elif msg.audio:
                        await send_client.send_audio(dest_chat, file_path, caption=final_caption)
                    elif msg.photo:
                        await send_client.send_photo(dest_chat, file_path, caption=final_caption)
                        
                    if file_path and os.path.exists(file_path): os.remove(file_path)
                    if thumb_path and os.path.exists(thumb_path): os.remove(thumb_path)
                        
                    await asyncio.sleep(2)
                    print(f"✅ Msg {current_id} Upload ho gaya! Next ->")
                    processed_count += 1

            except FloodWait as e:
                print(f"\n⚠️ Telegram speed limit! Wait kar raha hoon {e.value}s...")
                await asyncio.sleep(e.value + 5)
            except Exception as e:
                print(f"⏭️ Msg {current_id} par error aaya ({e}). Next ->")

        # Result Summary
        if bot_app.is_connected:
            if processed_count == 0:
                await message.reply_text("⚠️ **Task Khatam! Par ek bhi message gaya nahi.**\n*Iska matlab wahan koi valid messages the hi nahi (Khali the ya delete ho gaye).*")
            else:
                await message.reply_text(f"🎉 **Task Khatam!** Total {processed_count} messages bhej diye gaye.")
            
    except Exception as e:
        print(f"❌ Process error: {e}")
        if bot_app.is_connected:
            await message.reply_text("❌ Process me koi error aayi. Logs check karein.")

async def main():
    await user_app.start()
    await bot_app.start()
    print("\n🤖 SZX Master Bot Online! Go to Telegram and send /task")
    try:
        while True:
            await asyncio.sleep(3600)
    except KeyboardInterrupt: pass
    finally:
        await user_app.stop()
        await bot_app.stop()

# Execution
try: asyncio.get_event_loop().run_until_complete(main())
except Exception as e: print(f"Loop error: {e}")
