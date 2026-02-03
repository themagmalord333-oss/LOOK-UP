import os
import asyncio
import json
import threading
from flask import Flask
from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChannelInvalid

# --- 🌐 WEB SERVER (Render Ke Liye) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Running 24/7! 🚀"

def run_web():
    # Render automatically assigns a port via 'PORT' env var
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

# Start Web Server in Background Thread
t = threading.Thread(target=run_web)
t.daemon = True
t.start()

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"

# 🆕 LATEST SESSION STRING
SESSION_STRING = "BQI5Xz4Aadlw9vG6YxAqXFSjtHfhp-i1vs-tVvj5AAUdj2O-rYBlNSSwyaZ5HBffoWHRb7AflIHLtrHUPQJuj65Al3nuxinpPa_8-leNVZiExVIqEpHvt6z0JwIb473dAhzqh5du0Dj5QPxVALpsfkqGPvOfLqkjBl2gF7d6hlLwe7amwabCloEXyNDnZbRtSuwtqAAj1_Mtmu4B0EojJw8VFRNXSLu66zR0vz1J1i7hb7GH_pFVTezy0xNAhKA5_HfNML5g2ZsNTMld1D8mWBJLp853wzZr0W-fVRBVnDiIMmsnAgP2hVok6EnrLpOOa5FtqM9hCjTUA071pee3SjJFwRu0pQAAAAFJSgVkAA"

# 🎯 TARGET SETTINGS
TARGET_BOT_USERNAME = "Backupinfo69_bot"
SEARCH_GROUP_ID = -1003320004816 

# --- 🔐 SECURITY SETTINGS ---
ALLOWED_GROUPS = [-1003387459132] 

# Force Sub Channels
FSUB_CONFIG = [
    {"username": "Anysnapupdate", "link": "https://t.me/Anysnapupdate"},
    {"username": "Anysnapsupport", "link": "https://t.me/Anysnapsupport"}
]

app = Client("anysnap_secure_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- HELPER: CHECK IF USER JOINED ---
async def check_user_joined(client, user_id):
    missing = False
    for ch in FSUB_CONFIG:
        try:
            member = await client.get_chat_member(ch["username"], user_id)
            if member.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
                missing = True
                break
        except UserNotParticipant:
            missing = True
            break
        except Exception:
            pass 
    return not missing 

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def show_dashboard(client, message):
    
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text(
            "🚫 **Access Denied!**\n\n"
            "Bot use karne ke liye pehle niche diye gaye channels join karein:\n\n"
            "📢 **[Click to Join Updates](https://t.me/Anysnapupdate)**\n"
            "👥 **[Click to Join Support](https://t.me/Anysnapsupport)**\n\n"
            "__Join karne ke baad dubara /start dabayein.__",
            disable_web_page_preview=True
        )

    text = (
        "📖 **ANYSNAP BOT DASHBOARD**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📢 **Updates:** [Join Here](https://t.me/Anysnapupdate)\n"
        "👥 **Support:** [Join Here](https://t.me/Anysnapsupport)\n"
        "━━━━━━━━━━━━━━━━━━\n\n"
        "🔍 **Available Commands:**\n"
        "📱 `/num [number]`\n"
        "🆔 `/aadhaar [uid]`\n"
        "🏢 `/gst [no]`\n"
        "🏦 `/ifsc [code]`\n"
        "💰 `/upi [id]`\n"
        "💸 `/fam [id]`\n"
        "🚗 `/vehicle [plate]`\n"
        "✈️ `/tg [username]`\n"
        "🕵️ `/trace [num]`\n"
        "📧 `/gmail [email]`\n\n"
        "**⚠️ Note:** Results are auto-deleted after 30 seconds.\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚡ **Designed & Powered by @MAGMAxRICH**"
    )
    await message.reply_text(text, disable_web_page_preview=True)

# --- MAIN LOGIC ---
@app.on_message(filters.command(["num", "aadhaar", "gst", "ifsc", "upi", "fam", "vehicle", "tg", "trace", "gmail"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def process_request(client, message):
    
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text(
            "🚫 **Access Denied!**\n\n"
            "Result dekhne ke liye pehle join karein:\n\n"
            "➡️ **[Join Update Channel](https://t.me/Anysnapupdate)**\n"
            "➡️ **[Join Support Group](https://t.me/Anysnapsupport)**\n\n"
            f"__Join karne ke baad wapas `/{message.command[0]}` bhejein.__",
            disable_web_page_preview=True
        )

    if len(message.command) < 2:
        return await message.reply_text(f"❌ **Data Missing!**\nUsage: `/{message.command[0]} <value>`")

    status_msg = await message.reply_text(f"🔍 **Searching via Anysnap...**")
    
    # --- 🛡️ ACCESS CHECK ---
    try:
        await client.get_chat(SEARCH_GROUP_ID)
    except (PeerIdInvalid, ChannelInvalid):
        await status_msg.edit(
            f"❌ **Connection Error!**\n\n"
            f"Bot (Account) target group me joined nahi hai.\n"
            f"**Action:** Please manually join the group (`{SEARCH_GROUP_ID}`) with the account linked to the Session String."
        )
        return
    except Exception as e:
        await status_msg.edit(f"❌ **Check Error:** {str(e)}")
        return

    try:
        # 1. Send Message to the SEARCH GROUP
        sent_req = await client.send_message(SEARCH_GROUP_ID, message.text)
        
        target_response = None
        
        # --- WAIT LOOP ---
        for attempt in range(20): 
            await asyncio.sleep(2.5) 
            
            async for log in client.get_chat_history(SEARCH_GROUP_ID, limit=5):
                if log.from_user and log.from_user.username == TARGET_BOT_USERNAME:
                    if log.reply_to_message_id == sent_req.id:
                        
                        text_content = (log.text or log.caption or "").lower()
                        ignore_words = ["wait", "processing", "searching", "scanning", "generating", "loading", "checking"]
                        
                        if any(word in text_content for word in ignore_words):
                            await status_msg.edit(f"⏳ **Anysnap Processing... (Attempt {attempt+1})**")
                            break 
                        
                        target_response = log
                        break 
            
            if target_response: break
        
        if not target_response:
            await status_msg.edit("❌ **Timeout:** Target bot ne group me reply nahi diya.")
            return

        # --- Data Handling ---
        raw_text = ""
        if target_response.document:
            await status_msg.edit("📂 **Downloading File...**")
            file_path = await client.download_media(target_response)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            os.remove(file_path)
        elif target_response.photo:
            raw_text = target_response.caption or ""
        elif target_response.text:
            raw_text = target_response.text

        if not raw_text or len(raw_text.strip()) < 5:
            await status_msg.edit("❌ **No Data Found**")
            return

        # --- 🧹 CLEANING & FORMATTING ---
        lines = raw_text.splitlines()
        clean_data_list = []
        
        for line in lines:
            line = line.strip()
            if not line: continue 

            # Remove specific watermarks but keep Data keys
            if "@" in line or "Designed & Powered" in line or "DeepTrace" in line:
                if not any(k in line for k in ["Name", "Number", "Vehicle", "GST", "IFSC", "Email", "Status", "DOB", "Address", "Mobile"]):
                    continue
            
            clean_data_list.append(line)

        # --- 🛠️ JSON FORMATTING (Easy Read Mode) ---
        json_data = {
            "status": "success",
            "service": message.command[0],
            "query": " ".join(message.command[1:]),
            "data": clean_data_list,  
            "powered_by": "@MAGMAxRICH"
        }
        
        final_json_output = f"```json\n{json.dumps(json_data, indent=4, ensure_ascii=False)}\n```"

        await status_msg.delete()
        result_msg = await message.reply_text(final_json_output)
        
        # --- ⏱️ AUTO DELETE (30 Seconds) ---
        await asyncio.sleep(30)
        try:
            await result_msg.delete()
        except:
            pass 

    except Exception as e:
        await status_msg.edit(f"❌ **Error:** {str(e)}")

print("🚀 Secure ANYSNAP (Flask + JSON Mode) is Live!")
app.run()
