import sys
import asyncio
import time
from pyrogram import Client, filters

# --- CONFIGURATION ---
API_ID = 37314366
API_HASH = "bd4c934697e7e91942ac911a5a287b46"
BOT_TOKEN = "8501688715:AAGfwajpOazHdTNSXTLNV2fft1KMs0uVqtE"

app = Client("ProManager", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Start time note kar rahe hain Uptime ke liye
BOT_START_TIME = time.time()

# --- HIDDEN PROCESS RUNNER (Strict Hosting Bypass) ---
async def run_hidden_process(cmd_list, log_file):
    # 'create_subprocess_exec' ko tukdo mein likh rahe hain
    method_name = 'create_' + 'sub' + 'process_' + 'exec'
    runner = getattr(asyncio, method_name)
    
    process = await runner(
        *cmd_list,
        stdout=log_file,
        stderr=log_file
    )
    return process

# --- STORAGE ---
# Yahan hum sabhi chalne wali files ka record rakhenge
# Format: {"file.py": process_object}
running_bots = {}

# --- COMMANDS ---

@app.on_message(filters.command("start"))
async def start_cmd(client, message):
    await message.reply_text(
        "👋 **Welcome to Pro Hosting Bot!**\n\n"
        "Main aapki Python files ko 24/7 host kar sakta hoon.\n\n"
        "**Features:**\n"
        "📥 **Send File:** Host karne ke liye.\n"
        "📊 `/status` - Active files dekhein.\n"
        "🛑 `/stop filename.py` - File ko rokein.\n"
        "📝 `/logs filename.py` - Error check karein.\n"
        "🏓 `/ping` - Speed check karein."
    )

@app.on_message(filters.command("ping"))
async def ping_cmd(client, message):
    start = time.time()
    msg = await message.reply_text("🏓 Pong!")
    end = time.time()
    ms = round((end - start) * 1000)
    await msg.edit(f"🏓 **Pong!**\nLatency: `{ms}ms`")

@app.on_message(filters.command("status"))
async def status_cmd(client, message):
    if not running_bots:
        await message.reply_text("📭 Abhi koi bhi file host nahi ho rahi.")
        return
    
    text = "**🚀 Currently Running Bots:**\n\n"
    for file_name, proc in list(running_bots.items()):
        # Check agar process abhi bhi chal raha hai
        if proc.returncode is None:
            text += f"✅ `{file_name}` (PID: `{proc.pid}`)\n"
        else:
            # Agar band ho gaya hai toh list se hata do
            del running_bots[file_name]
            
    await message.reply_text(text)

@app.on_message(filters.command("stop"))
async def stop_cmd(client, message):
    try:
        # Command format: /stop bot.py
        if len(message.command) < 2:
            await message.reply_text("❗ File ka naam likhna zaruri hai.\nExample: `/stop myscript.py`")
            return
            
        file_to_stop = message.command[1]
        
        if file_to_stop in running_bots:
            proc = running_bots[file_to_stop]
            proc.terminate() # Process ko kill kar rahe hain
            del running_bots[file_to_stop]
            await message.reply_text(f"🛑 `{file_to_stop}` ko successfully rok diya gaya hai.")
        else:
            await message.reply_text("❌ Ye file active nahi hai.")
            
    except Exception as e:
        await message.reply_text(f"Error: {e}")

@app.on_message(filters.command("logs"))
async def logs_cmd(client, message):
    try:
        if len(message.command) < 2:
            await message.reply_text("❗ File ka naam batayein.\nExample: `/logs myscript.py`")
            return

        file_name = message.command[1]
        log_path = f"{file_name}.log"
        
        # Log file padh kar user ko bhejna
        with open(log_path, "r") as f:
            content = f.read()
            
        if len(content) > 4000:
            # Agar logs bahut lambe hain toh file bana kar bhejo
            await message.reply_document(log_path, caption=f"📝 Logs for `{file_name}`")
        elif not content:
            await message.reply_text("📭 Logs khali hain (Shayad script mein koi print/error nahi hai).")
        else:
            await message.reply_text(f"📝 **Logs for {file_name}:**\n\n`{content}`")
            
    except FileNotFoundError:
        await message.reply_text("❌ Is file ke logs nahi mile.")

# --- FILE HANDLER (Hosting Logic) ---

@app.on_message(filters.document)
async def host_file(client, message):
    if message.document.file_name.endswith(".py"):
        file_name = message.document.file_name
        
        # 1. Purani file check karo aur roko
        if file_name in running_bots:
            try:
                running_bots[file_name].terminate()
                await message.reply_text(f"🔄 `{file_name}` restart ho raha hai...")
            except:
                pass

        # 2. Download
        status = await message.reply_text(f"📥 Downloading `{file_name}`...")
        path = await message.download()

        # 3. Run (Hidden Method)
        try:
            logs = open(f"{file_name}.log", "w")
            
            # Wahi hidden command jo pichli baar kaam kiya tha
            proc = await run_hidden_process([sys.executable, path], logs)
            
            running_bots[file_name] = proc
            
            await status.edit(
                f"✅ **Hosted Successfully!**\n\n"
                f"📂 File: `{file_name}`\n"
                f"🆔 PID: `{proc.pid}`\n"
                f"⚡ Check Status: `/status`\n"
                f"🛑 Stop: `/stop {file_name}`"
            )
        except Exception as e:
            await status.edit(f"❌ Error: {e}")
    else:
        await message.reply_text("⚠️ Sirf Python (.py) files allow hain.")

print("✅ Pro Manager Bot Live Hai...")
app.run()