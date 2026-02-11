import os
import asyncio
import json
import threading
from flask import Flask
from pyrogram import Client, filters, enums
from pyrogram.errors import UserNotParticipant, PeerIdInvalid, ChannelInvalid

# --- 🌐 WEB SERVER (For 24/7 Hosting) ---
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is Running 24/7! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

t = threading.Thread(target=run_web)
t.daemon = True
t.start()

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"

# 🆕 LATEST SESSION STRING
SESSION_STRING = "BQI5Xz4AmzwL4r48Fh3FFYkbXAvACVzMqb67stPRsvrIWKG1c0R83OANpXF0Vn-igy4HFDZhGAjFGRpys1mU9xL6Qwa4lhRQjzV6oFYN_uj9o9lGuRfxQlC18Iws1vdRdBR_MIw6Y9wWnYVey8eZI8zdEh1Gri23gIMjtsR9iErjrn6m4LDvRAGa50wxq126uu03GnxhcKDwLoD4ymjYLjNt17E0PdWolHvJEbl4RGVd7w2aaf3ZtP0KYhQadDIas4BDObkKR-8EQnNAtmL60x0BxAzdBrIS9oBhiaxHKvNJEf8lmxGb4WpGFV9-dCtrpYFI2zrSwpGC_Z_qoFjCkqabPDvFZgAAAAFJSgVkAA"

# 🎯 UPDATED TARGET SETTINGS
TARGET_BOT_USERNAME = "AdvancedInfoV2bot"
SEARCH_GROUP_ID = -1003227082022 

# --- 🔐 SECURITY & PRIVATE FSUB ---
ALLOWED_GROUPS = [-1003387459132] 

# Private Channel Settings
FSUB_CHANNELS = [
    {"id": -1003892920891, "link": "https://t.me/+Om1HMs2QTHk1N2Zh"}
]

app = Client("anysnap_secure_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- HELPER: CHECK JOIN ---
async def check_user_joined(client, user_id):
    for ch in FSUB_CHANNELS:
        try:
            member = await client.get_chat_member(ch["id"], user_id)
            if member.status in [enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED]:
                return False
        except (UserNotParticipant, PeerIdInvalid):
            return False
        except Exception:
            pass 
    return True

# --- DASHBOARD ---
@app.on_message(filters.command(["start", "help", "menu"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def show_dashboard(client, message):
    if not await check_user_joined(client, message.from_user.id):
        buttons = "\n".join([f"➡️ [Join Channel]({ch['link']})" for ch in FSUB_CHANNELS])
        return await message.reply_text(
            f"🚫 **Access Denied!**\n\nBot use karne ke liye join karein:\n{buttons}\n\nJoin karne ke baad /start karein.",
            disable_web_page_preview=True
        )

    text = (
        "📖 **ANYSNAP DASHBOARD**\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "🔍 **Commands:** `/num`, `/vehicle`, `/aadhaar`, `/gst`, `/upi`\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "⚡ **Powered by @MAGMAxRICH**"
    )
    await message.reply_text(text, disable_web_page_preview=True)

# --- MAIN LOGIC (JSON & CREDIT CHANGE) ---
@app.on_message(filters.command(["num", "aadhaar", "gst", "ifsc", "upi", "fam", "vehicle", "tg", "trace", "gmail"], prefixes="/") & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def process_request(client, message):
    if not await check_user_joined(client, message.from_user.id):
        return await message.reply_text("🚫 **Pehle Channel Join Karein!**")

    if len(message.command) < 2:
        return await message.reply_text(f"❌ Usage: `/{message.command[0]} <value>`")

    status_msg = await message.reply_text(f"🔍 **Searching via Anysnap...**")

    try:
        # Request send karna
        sent_req = await client.send_message(SEARCH_GROUP_ID, message.text)
        target_response = None

        # Wait Loop for @AdvancedInfoV2bot
        for attempt in range(20): 
            await asyncio.sleep(2.5) 
            async for log in client.get_chat_history(SEARCH_GROUP_ID, limit=8):
                if log.from_user and log.from_user.username == TARGET_BOT_USERNAME:
                    # Reply check karna
                    if log.reply_to_message_id == sent_req.id:
                        text_content = (log.text or log.caption or "").lower()
                        if any(word in text_content for word in ["wait", "processing", "searching"]):
                            continue 
                        target_response = log
                        break 
            if target_response: break

        if not target_response:
            return await status_msg.edit("❌ **Timeout:** Target bot ne reply nahi diya.")

        # Data Extraction
        raw_text = ""
        if target_response.document:
            file_path = await client.download_media(target_response)
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw_text = f.read()
            os.remove(file_path)
        else:
            raw_text = target_response.text or target_response.caption or ""

        # --- CLEANING & JSON TRANSFORMATION ---
        # Kisi bhi purane credit ko apne credit se badalna
        clean_text = raw_text.replace("@Zrov_Clan", "@MAGMAxRICH").replace("@AdvancedInfoV2bot", "@MAGMAxRICH")
        
        lines = [line.strip() for line in clean_text.splitlines() if line.strip()]
        results_list = []
        current_item = {}

        for line in lines:
            if ":" in line:
                key, val = line.split(":", 1)
                k = key.strip().lower()
                v = val.strip()
                # Naya record identify karna (agar Mobile ya Name key dubara aaye)
                if k in ["mobile", "name", "id"] and k in current_item:
                    results_list.append(current_item)
                    current_item = {}
                current_item[k] = v

        if current_item:
            results_list.append(current_item)

        # Final JSON Structure
        final_json = {
            "status": "success",
            "count": len(results_list),
            "results": results_list,
            "credit": "@MAGMAxRICH"
        }

        await status_msg.delete()
        json_output = json.dumps(final_json, indent=4, ensure_ascii=False)
        result_msg = await message.reply_text(
            f"**Result:**\n```json\n{json_output}\n```\n\n@MAGMAxRICH"
        )

        # Auto Delete result after 30 seconds
        await asyncio.sleep(30)
        await result_msg.delete()

    except Exception as e:
        await status_msg.edit(f"❌ **Error:** {str(e)}")

print("🚀 ANYSNAP Updated JSON Mode Live!")
app.run()
