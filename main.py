import os
import asyncio
import json
import re
import threading
from flask import Flask
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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
# Aapka Session String
SESSION_STRING = "BQI5Xz4ANzYEjiKIML0uMU9tojksdxKz_bCurzC00eBbvDLQZan_bwZtMzXJzHJaybTK_HK1Q6TLbbfGXguF4W_s7gbSZaOESUHERMDJJxk_v3dM_7fbuCyKTP0ajf9NS9sbPYoK2Tiq9s91aJln1vYuQ8YlN3SBgwKcYOwwXTFv_WhWsF4ZnT4GQZEAU6cdudoEQmfTrXAh_plktB1TwrDd57rh5ulwyCW37uJyW_OwqdC1moXgrWzV4mj4Gx6_ghkolzi7AhfUpk_emqjMhBj5x7-sUB5SUwcbdWCqWVKivfu3Wu0uE4EVCcpVHsEycT3HPr-chNqdpjLRTIyD-Euc3w3gkwAAAAFJSgVkAA"

TARGET_BOT_USERNAME = "Zeroo_osint_bot" 
SEARCH_GROUP_ID = -1003322045321
SEARCH_GROUP_USERNAME = "f4x_empirebot"

ALLOWED_GROUPS = [-1003387459132]
FSUB_CHANNELS = [{"id": -1003892920891, "link": "https://t.me/+Om1HMs2QTHk1N2Zh"}]

app = Client("anysnap_secure_bot", api_id=API_ID, api_hash=API_HASH, session_string=SESSION_STRING)

# --- 🧠 BROKEN DATA EXTRACTOR ---
def extract_broken_data(text):
    results = []
    
    # 1. Sabse pehle agar Valid JSON mil jaye toh wahin se lelo
    try:
        match = re.search(r'(\[[\s\S]*\])', text)
        if match:
            return json.loads(match.group(1))
    except:
        pass # JSON fail hua toh niche wala Jugaad chalega

    # 2. JUGAAD: Regex se Key-Value pairs dhundho (Chahe JSON ho ya Text)
    # Ye pattern "key": "value" aur Key: Value dono ko pakdega
    raw_entries = re.split(r'\}|━━━━━━━━━━━━━━━━━━━━', text) # Har object ke baad split karo

    for entry in raw_entries:
        if not entry.strip(): continue
        
        data = {}
        # Regex map for both JSON style ("key": "val") and Text style (Key: Val)
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

        found_any = False
        for key, patterns in mappings.items():
            for pat in patterns:
                match = re.search(pat, entry, re.IGNORECASE)
                if match:
                    val = match.group(1).strip()
                    # Cleanup values (remove commas or quotes if leaked)
                    val = val.rstrip('",')
                    if val and val.lower() != "n/a":
                        data[key] = val
                        found_any = True
                    break
        
        if found_any:
            results.append(data)

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
    status_msg = await message.reply_text(f"🔍 **Searching:** `{query_val}`...\n⏳ *Fetching data...*")

    try:
        try: chat = await client.get_chat(SEARCH_GROUP_USERNAME)
        except: chat = await client.get_chat(SEARCH_GROUP_ID)

        sent_req = await client.send_message(chat.id, f"/num {query_val}")
        target_response = None

        # 60 Sec Wait Loop
        for _ in range(30): 
            await asyncio.sleep(2) 
            async for log in client.get_chat_history(chat.id, limit=10):
                if log.reply_to_message_id == sent_req.id:
                    txt = (log.text or log.caption or "").lower()
                    if any(w in txt for w in ["searching", "processing", "wait"]): continue
                    
                    # Agar 'mobile' ya 'address' jaisa shabd dikhe, toh result manlo
                    if "mobile" in txt or "address" in txt or "[" in txt:
                        target_response = log
                        break
            if target_response: break

        if not target_response:
            return await status_msg.edit("❌ **Timeout:** Target bot ne reply nahi diya.")

        raw_text = target_response.text or target_response.caption or ""
        
        # Asli Magic: Broken Data Extractor
        final_data = extract_broken_data(raw_text)

        if not final_data:
            return await status_msg.edit(f"❌ **Error:** Data samajh nahi aaya.\nRaw: `{raw_text[:50]}...`")

        # Output
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
        await message.reply_text(
            output_ui,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📋 COPY CODE", switch_inline_query_current_chat=json_box)]])
        )

    except Exception as e:
        await status_msg.edit(f"❌ **Error:** {str(e)}")

print("🚀 Broken JSON Handler Live!")
app.run()
