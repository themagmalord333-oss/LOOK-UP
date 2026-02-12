import os
import asyncio
import json
import re
import threading
from flask import Flask
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# --- 🛠️ FIX FOR PYTHON 3.10+ / 3.14 EVENT LOOP ERROR ---
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass

# Force create an event loop if one doesn't exist
try:
    loop = asyncio.get_running_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
# -------------------------------------------------------

# --- 🌐 WEB SERVER ---
web_app = Flask(__name__)
@web_app.route('/')
def home(): return "Bot is Online! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

threading.Thread(target=run_web, daemon=True).start()

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"
SESSION_STRING = "BQI5Xz4AaDFKlxzx_muIPYRzRIyyvWNmtF2NLY6pdaohx8V11Md5_7TPwIW3sT-Tky3rKh6qOh9ARJDsB9ZBK8KstH5EkSAi6wX4edFpThdUKyahCAbjlj7dp9GK5KOR9JNjjxRTIMRxelhkFp7uErgEL86oYPB4NKMknMqol-kzuLathqALqAAEK3woiZn_af73k8dD5wTWoXbZsWu6UJZPfE2EauvJxVhvvx8HY7ojt7YpmCSel-meMxnIzv7gi5AiEveSdT_Kk_3Ntj7h5bxFb_rcEDo0kOvrvFx6ibJeu8XFdJ8U9wD4BmgbiGQlsvghGHj3gY5-t0969-4VEig-3zSl-QAAAAFJSgVkAA"

TARGET_BOT_USERNAME = "Zeroo_osint_bot"
SEARCH_GROUP_ID = -1003322045321
SEARCH_GROUP_USERNAME = "f4x_empirebot"

ALLOWED_GROUPS = [-1003387459132]
FSUB_CHANNELS = [{"id": -1003892920891, "link": "https://t.me/+Om1HMs2QTHk1N2Zh"}]

# 👑 OWNER SETTINGS
OWNER_ID = 8081343902
STICKER_FILE = "anim_sticker.txt"

app = Client("anysnap_secure_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- 👋 START COMMAND ---
@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    name = message.from_user.first_name
    
    if user_id == OWNER_ID:
        await message.reply_text(
            f"👑 **Welcome Boss {name}!**\n"
            f"🆔 Your ID: `{user_id}` (Matched)\n\n"
            f"**🎛️ Owner Commands:**\n"
            f"🔹 `/setanim` - (Reply to Sticker) Set Waiting Animation\n"
            f"🔹 `/resetanim` - Reset Animation\n"
            f"🔹 `/num <number>` - Search Number"
        )
    else:
        for ch in FSUB_CHANNELS:
            try: await client.get_chat_member(ch["id"], user_id)
            except: 
                return await message.reply_text(f"👋 **Hello {name}!**\n🚫 Access Denied.\nPlease Join: {ch['link']}")
        
        await message.reply_text(f"👋 **Hello {name}!**\n🆔 ID: `{user_id}`\n\n✅ Bot is Ready. Use `/num <number>` to search.")

# --- 🎭 MASTI FEATURE ---
def get_waiting_sticker():
    if os.path.exists(STICKER_FILE):
        with open(STICKER_FILE, "r") as f:
            return f.read().strip()
    return None

@app.on_message(filters.command("setanim") & filters.user(OWNER_ID))
async def set_animation(client, message):
    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await message.reply("❌ **Galti!** Pehle ek Sticker bhejo, fir us par **Reply** karke `/setanim` likho.")
    
    sticker_id = message.reply_to_message.sticker.file_id
    with open(STICKER_FILE, "w") as f:
        f.write(sticker_id)
    
    await message.reply("✅ **Animation Set!**\nAb jab aap (`Owner`) search karenge toh ye sticker dikhega.")

@app.on_message(filters.command("resetanim") & filters.user(OWNER_ID))
async def reset_animation(client, message):
    if os.path.exists(STICKER_FILE):
        os.remove(STICKER_FILE)
    await message.reply("🔄 **Reset!** Normal text wapas aa gaya.")

# --- 🧠 BROKEN DATA EXTRACTOR ---
def extract_broken_data(text):
    results = []
    try:
        match = re.search(r'(\[[\s\S]*\])', text)
        if match: return json.loads(match.group(1))
    except: pass 

    raw_entries = re.split(r'\}|━━━━━━━━━━━━━━━━━━━━', text)
    for entry in raw_entries:
        if not entry.strip(): continue
        data = {}
        mappings = {
            "name": [r'"name":\s*"(.*?)"', r'Name:\s*(.*)'],
            "mobile": [r'"mobile":\s*"(.*?)"', r'Mobile:\s*(.*)'],
            "fname": [r'"fname":\s*"(.*?)"', r'Father Name:\s*(.*)'],
            "address": [r'"address":\s*"(.*?)"', r'Address:\s*(.*)'],
            "circle": [r'"circle":\s*"(.*?)"', r'Circle:\s*(.*)'],
            "alt": [r'"alt":\s*"(.*?)"', r'Alt Mobile:\s*(.*)'],
            "email": [r'"email":\s*"(.*?)"', r'Email:\s*(.*)'],
            "id": [r'"id":\s*"(.*?)"', r'ID:\s*(.*)']
        }
        found = False
        for key, patterns in mappings.items():
            for pat in patterns:
                match = re.search(pat, entry, re.IGNORECASE)
                if match:
                    val = match.group(1).strip().rstrip('",')
                    if val and val.lower() != "n/a":
                        data[key] = val
                        found = True
                    break
        if found: results.append(data)
    return results

# --- MAIN LOGIC ---
@app.on_message(filters.command(["num", "aadhaar", "vehicle", "trace"]) & (filters.private | filters.chat(ALLOWED_GROUPS)))
async def process_request(client, message):
    for ch in FSUB_CHANNELS:
        try: await client.get_chat_member(ch["id"], message.from_user.id)
        except: return await message.reply_text(f"🚫 **Access Denied!**\nJoin: {ch['link']}")

    if len(message.command) < 2:
        return await message.reply_text(f"❌ Usage: `/{message.command[0]} <value>`")

    query_val = message.command[1]
    user_id = message.from_user.id
    
    sticker_id = get_waiting_sticker()
    if user_id == OWNER_ID and sticker_id:
        status_msg = await message.reply_sticker(sticker_id)
    else:
        status_msg = await message.reply_text(f"🔍 **Searching:** `{query_val}`...\n⏳ *Fetching data...*")

    try:
        try: chat = await client.get_chat(SEARCH_GROUP_USERNAME)
        except: chat = await client.get_chat(SEARCH_GROUP_ID)

        sent_req = await client.send_message(chat.id, f"/num {query_val}")
        target_response = None

        for _ in range(30): 
            await asyncio.sleep(2) 
            async for log in client.get_chat_history(chat.id, limit=10):
                if log.reply_to_message_id == sent_req.id:
                    txt = (log.text or log.caption or "").lower()
                    if any(w in txt for w in ["searching", "processing", "wait"]): continue
                    
                    if "mobile" in txt or "address" in txt or "[" in txt:
                        target_response = log
                        break
            if target_response: break

        if not target_response:
            await status_msg.delete()
            return await message.reply_text("❌ **Timeout:** Target bot ne reply nahi diya.")

        raw_text = target_response.text or target_response.caption or ""
        final_data = extract_broken_data(raw_text)

        if not final_data:
            await status_msg.delete()
            return await message.reply_text(f"❌ **Error:** Data samajh nahi aaya.\nRaw: `{raw_text[:50]}...`")

        json_box = json.dumps(final_data, indent=2, ensure_ascii=False)
        output_ui = (
            f"👤 **{message.from_user.first_name}**\n"
            f"🔢 `{query_val}`\n\n"
            f"📂 **Number Information**\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"📝 **JSON Response:**\n"
            f"```json\n{json_box}\n```\n"
            f"👊 **MADE BY @MAGMAxRICH**"
        )

        await status_msg.delete()
        final_msg = await message.reply_text(
            output_ui,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 COPY CODE", switch_inline_query_current_chat=json_box)]])
        )

        await asyncio.sleep(30)
        await final_msg.delete()

    except Exception as e:
        await status_msg.delete()
        await message.reply_text(f"❌ **Error:** {str(e)}")

print("🚀 Bot Live: Python 3.14 Event Loop Patch Applied!")
app.run()
