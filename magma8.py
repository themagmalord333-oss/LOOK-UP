import requests
import json
import time
import random
import string
from datetime import datetime, date

# Bot Configuration
TOKEN = "8501688715:AAElcns0Mv3Ks-Ffh4NQm34WM0u6MjcSyiY"
API_URL = "https://x2-proxy.vercel.app/api?num="
AADHAR_API_URL = "http://antifiednullapi.vercel.app/search?id="
SNAPCHAT_API_URL = "https://web-production-3abfa.up.railway.app/profile/"
ADMIN_ID = 8081343902

# Group and Channel
GROUP = "@Anysnapsupport"
CHANNEL = "@Anysnapupdate"
USE_ME_THERE = "@Anysnapsupport"

# Load user data
try:
    with open("users.json", "r") as f:
        users = json.load(f)
except:
    users = {}

# Load redeem codes data
try:
    with open("redeem_codes.json", "r") as f:
        redeem_codes = json.load(f)
except:
    redeem_codes = {}

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)

def save_redeem_codes():
    with open("redeem_codes.json", "w") as f:
        json.dump(redeem_codes, f, indent=4)

# ✅ Check Membership
def check_membership(user_id):
    try:
        group_resp = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getChatMember",
            params={"chat_id": GROUP, "user_id": user_id},
            timeout=10
        ).json()
        
        channel_resp = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getChatMember",
            params={"chat_id": CHANNEL, "user_id": user_id},
            timeout=10
        ).json()
        
        if not group_resp.get('ok') or not channel_resp.get('ok'):
            return False
        
        group_status = group_resp['result'].get('status', 'left')
        channel_status = channel_resp['result'].get('status', 'left')
        
        group_ok = group_status in ['member', 'administrator', 'creator']
        channel_ok = channel_status in ['member', 'administrator', 'creator']
        
        return group_ok and channel_ok
        
    except Exception as e:
        print(f"Membership check error: {e}")
        return False

# Send Message
def send_msg(chat_id, text, markup=None, reply_to=None):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
    if markup:
        data["reply_markup"] = json.dumps(markup)
    if reply_to:
        data["reply_to_message_id"] = reply_to
    try:
        resp = requests.post(url, json=data, timeout=5)
        return resp.json()
    except:
        return {"ok": False}

# Keyboards
def force_join_kb():
    return {
        "inline_keyboard": [
            [{"text": "👥 JOIN SUPPORT GROUP", "url": f"https://t.me/{GROUP[1:]}"}],
            [{"text": "📢 JOIN UPDATE CHANNEL", "url": f"https://t.me/{CHANNEL[1:]}"}],
            [{"text": "✅ VERIFY MEMBERSHIP", "callback_data": "verify_membership"}]
        ]
    }

def join_group_only_kb():
    return {
        "inline_keyboard": [
            [{"text": "🤖 USE ME IN GROUP", "url": f"https://t.me/{USE_ME_THERE[1:]}"}],
            [{"text": "➕ ADD ME IN YOUR GROUP", "url": "https://t.me/Mikaaichatbot?startgroup=true"}]
        ]
    }

def main_menu_kb(user_id):
    user = users.get(str(user_id), {})
    credits = user.get("credits", 0)
    refs = user.get("referrals", 0)
    
    keyboard = [
        [{"text": "📱 NUMBER INFO", "callback_data": "search"}],
        [{"text": "🆔 AADHAR INFO", "callback_data": "aadhar_search"}],
        [{"text": "👻 SNAPCHAT INFO", "callback_data": "snap_search"}],
        [{"text": f"💰 MY CREDITS: {credits}", "callback_data": "mycredits"}],
        [{"text": f"👥 REFERRAL: {refs}", "callback_data": "referral"}],
        [{"text": "🎟️ REDEEM CODE", "callback_data": "redeem_code"}],
        [{"text": "🔄 VERIFY AGAIN", "callback_data": "verify_membership"}],
        [{"text": "🆘 HELP", "callback_data": "help"}]
    ]
    
    return {"inline_keyboard": keyboard}

def get_or_create_user(user_id, name):
    user_str = str(user_id)
    
    if user_str not in users:
        users[user_str] = {
            "credits": 10,
            "referrals": 0,
            "name": name,
            "last_bonus": "",
            "joined_date": str(date.today()),
            "membership_verified": True,
            "first_search_date": str(date.today()),
            "redeemed_codes": []
        }
        save_users()
        print(f"✅ Auto-created user: {name} ({user_id})")
    
    return users[user_str]

def is_group_chat(chat_id):
    try:
        chat_info = requests.get(
            f"https://api.telegram.org/bot{TOKEN}/getChat",
            params={"chat_id": chat_id},
            timeout=5
        ).json()
        
        if chat_info.get('ok'):
            chat_type = chat_info['result'].get('type', 'private')
            return chat_type in ['group', 'supergroup']
        return False
    except:
        return False

# ✅ Handle /num Command
def handle_num_command(user_id, name, text, chat_id=None, reply_to=None):
    chat_id = chat_id or user_id
    
    if not is_group_chat(chat_id) and user_id != ADMIN_ID:
        handle_private_message(user_id, name, text, chat_id, reply_to)
        return
    
    parts = text.split()
    
    if len(parts) == 1:
        msg = """
🔍 <b>NUMBER SEARCH COMMAND</b>
━━━━━━━━━━━━━━━━━━
<b>Powered by @MAGMAxRICH</b>
━━━━━━━━━━━━━━━━━━

<b>Usage:</b>
<code>/num 9876543210</code>

<b>Examples:</b>
• <code>/num 9876543210</code>
• <code>/num 9123456789</code>
• <code>/num 7012345678</code>

━━━━━━━━━━━━━━━━━━
<b>Instructions:</b>
1️⃣ Send <code>/num [10-digit-number]</code>
2️⃣ Each search costs 1 credit
        """
        send_msg(chat_id, msg, None, reply_to)
        return
    
    number = parts[1]
    
    if len(number) >= 10 and number.isdigit():
        if len(number) > 10:
            number = number[:10]
            send_msg(chat_id, f"⚠️ Using first 10 digits: <code>{number}</code>", reply_to=reply_to)
        
        handle_search(user_id, name, number, chat_id, reply_to)
    else:
        error_msg = f"""
❌ <b>INVALID NUMBER FORMAT</b>

<code>{number}</code> is not valid!

<b>Correct Format:</b>
• 10 digits only
• No +, no spaces

<b>Example:</b>
<code>/num 9876543210</code>
        """
        send_msg(chat_id, error_msg, None, reply_to)

# ✅ Mobile Search Function - JSON FORMAT
def handle_search(user_id, name, number, chat_id=None, reply_to=None):
    chat_id = chat_id or user_id
    
    if not is_group_chat(chat_id) and user_id != ADMIN_ID:
        handle_private_message(user_id, name, number, chat_id, reply_to)
        return
    
    is_member = check_membership(user_id)
    
    if not is_member:
        msg = f"""
❌ <b>ACCESS DENIED!</b>

You must join group and channel to search.
        """
        send_msg(chat_id, msg, force_join_kb(), reply_to)
        return
    
    user = get_or_create_user(user_id, name)
    user["membership_verified"] = True
    user["name"] = name
    
    if user_id != ADMIN_ID and user.get("credits", 0) < 1:
        send_msg(chat_id, "❌ <b>Not enough credits!</b>\n\nYou have 0 credits left.", reply_to)
        send_msg(chat_id, "🏠 <b>Main Menu</b>", main_menu_kb(user_id), reply_to=reply_to)
        return
    
    if user_id != ADMIN_ID:
        user["credits"] -= 1
        save_users()
    
    send_msg(chat_id, "🔍 <b>Searching Mobile Number... Please wait</b>", reply_to=reply_to)
    
    try:
        resp = requests.get(f"{API_URL}{number}", timeout=15)
        
        if resp.status_code == 200:
            data = resp.json()
            
            results = []
            if isinstance(data, list):
                results = data
            elif isinstance(data, dict):
                if "result" in data:
                    results = data["result"]
                elif "data" in data:
                    results = data["data"]
                elif "results" in data:
                    results = data["results"]
            
            if isinstance(results, list) and len(results) > 0:
                total_results = len(results)
                
                # Create JSON structure
                json_data = {
                    "search_info": {
                        "mobile_number": number,
                        "search_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "total_records": total_results,
                        "credits_used": 1,
                        "searched_by": {
                            "user_id": str(user_id),
                            "name": name
                        }
                    },
                    "results": []
                }
                
                for idx, item in enumerate(results, 1):
                    if not isinstance(item, dict):
                        continue
                    
                    # Extract data
                    name_result = str(item.get('name', 'N/A')).strip()
                    
                    mobile_fields = ['mobile', 'smobile', 'phone', 'phonenumber', 'contact']
                    mobile = number
                    for field in mobile_fields:
                        if field in item:
                            mobile = str(item[field])
                            break
                    
                    father_fields = ['father_name', 'fname', 'father', 'fathername', 'parent']
                    father = 'N/A'
                    for field in father_fields:
                        if field in item:
                            father = str(item[field]).strip()
                            break
                    
                    address_fields = ['address', 'advert', 'location', 'add', 'addr']
                    address = 'N/A'
                    for field in address_fields:
                        if field in item:
                            address = str(item[field]).strip()
                            break
                    
                    aadhar_fields = ['id', 'aadhar', 'aadhaar', 'uid']
                    aadhar = 'N/A'
                    for field in aadhar_fields:
                        if field in item:
                            aadhar = str(item[field])
                            break
                    
                    alt_fields = ['alt_number', 'alt_mobile', 'alt', 'alternate', 'altphone']
                    alt = 'N/A'
                    for field in alt_fields:
                        if field in item:
                            alt = str(item[field])
                            break
                    
                    # Clean address
                    addr = address
                    separators = ['|', '@', '!', '#', '$', '%', '^', '&', '*', '~']
                    for sep in separators:
                        addr = addr.replace(sep, ', ')
                    addr = addr.replace('  ', ' ').replace(' ,', ',').strip()
                    
                    # Format Aadhar
                    aadhar_display = 'N/A'
                    if aadhar != 'N/A' and aadhar.isdigit():
                        a = str(aadhar)
                        if len(a) >= 12:
                            aadhar_display = f"{a[:4]} {a[4:8]} {a[8:12]}"
                        elif len(a) >= 10:
                            aadhar_display = a
                    
                    # Detect circle
                    circle = 'N/A'
                    circle_keywords = {
                        'Jharkhand': ['jharkhand', 'jh', 'ranchi', 'jamshedpur', 'dhanbad'],
                        'Bihar': ['bihar', 'bh', 'patna', 'gaya', 'muzaffarpur'],
                        'Uttar Pradesh': ['uttar pradesh', 'up', 'lucknow', 'kanpur', 'varanasi'],
                        'Delhi': ['delhi', 'new delhi', 'ncr'],
                        'Maharashtra': ['maharashtra', 'mh', 'mumbai', 'pune', 'nagpur'],
                        'West Bengal': ['west bengal', 'wb', 'kolkata', 'howrah', 'durgapur'],
                        'Rajasthan': ['rajasthan', 'rj', 'jaipur', 'jodhpur', 'udaipur'],
                        'Punjab': ['punjab', 'pb', 'chandigarh', 'amritsar', 'ludhiana']
                    }
                    
                    addr_lower = addr.lower()
                    for state, keywords in circle_keywords.items():
                        for keyword in keywords:
                            if keyword in addr_lower:
                                circle = state
                                break
                        if circle != 'N/A':
                            break
                    
                    # Add to results
                    result_entry = {
                        "record_no": idx,
                        "name": name_result if name_result != 'N/A' else 'Not Available',
                        "mobile": mobile,
                        "father_name": father if father != 'N/A' else 'Not Available',
                        "address": addr,
                        "aadhar": aadhar_display if aadhar_display != 'N/A' else 'Not Available',
                        "alternate_number": alt if alt != 'N/A' else 'Not Available',
                        "circle": circle
                    }
                    
                    json_data["results"].append(result_entry)
                
                # Send header
                header_msg = f"""
✅ <b>SEARCH COMPLETED - JSON FORMAT</b>
━━━━━━━━━━━━━━━━━━━━━━━━
📱 <b>Number Searched:</b> {number}
📊 <b>Total Results Found:</b> {total_results}
⏰ <b>Search Time:</b> {datetime.now().strftime("%H:%M:%S")}
━━━━━━━━━━━━━━━━━━━━━━━━
<b>Powered by @MAGMAxRICH</b>
                """
                send_msg(chat_id, header_msg, reply_to=reply_to)
                
                # Send JSON data in code block
                json_str = json.dumps(json_data, indent=2, ensure_ascii=False)
                
                # Telegram message limit is 4096 characters
                max_length = 4000
                if len(json_str) > max_length:
                    # Split into chunks
                    chunks = [json_str[i:i+max_length] for i in range(0, len(json_str), max_length)]
                    
                    for i, chunk in enumerate(chunks, 1):
                        chunk_msg = f"""
<b>JSON Data Part {i}/{len(chunks)}</b>
<pre><code class="language-json">
{chunk}
</code></pre>
━━━━━━━━━━━━━━━━━━━━━━━━
                        """
                        send_msg(chat_id, chunk_msg, reply_to=reply_to)
                else:
                    json_msg = f"""
<b>COMPLETE JSON DATA</b>
<pre><code class="language-json">
{json_str}
</code></pre>
━━━━━━━━━━━━━━━━━━━━━━━━
                    """
                    send_msg(chat_id, json_msg, reply_to=reply_to)
                
                # Send footer
                footer_msg = f"""
💰 <b>Credits Left:</b> {user['credits'] if user_id != ADMIN_ID else 'Unlimited'}
✅ <b>Search Completed Successfully</b>
━━━━━━━━━━━━━━━━━━━━━━━━
<b>How to use this data:</b>
1. Copy the entire JSON block
2. Use any JSON viewer or parser
3. All data is in structured format
━━━━━━━━━━━━━━━━━━━━━━━━
<b>Powered by @MAGMAxRICH</b>
                """
                send_msg(chat_id, footer_msg, reply_to=reply_to)
                
            else:
                result = f"""
❌ <b>NO DATA FOUND</b>
━━━━━━━━━━━━━━━━━━
📱 <b>Number Searched:</b> {number}
⚠️ <b>Status:</b> No records found in database
━━━━━━━━━━━━━━━━━━
<b>Credits Left:</b> {user['credits'] if user_id != ADMIN_ID else 'Unlimited'}
━━━━━━━━━━━━━━━━━━
<b>Powered by @MAGMAxRICH</b>
                """
                send_msg(chat_id, result, reply_to=reply_to)
        else:
            result = f"""
❌ <b>API CONNECTION ERROR</b>
━━━━━━━━━━━━━━━━━━
📱 <b>Number Searched:</b> {number}
⚠️ <b>Status:</b> API Error {resp.status_code}
━━━━━━━━━━━━━━━━━━
<b>Credits Left:</b> {user['credits'] if user_id != ADMIN_ID else 'Unlimited'}
━━━━━━━━━━━━━━━━━━
<b>Powered by @MAGMAxRICH</b>
            """
            send_msg(chat_id, result, reply_to=reply_to)
            
    except Exception as e:
        result = f"""
❌ <b>SEARCH ERROR</b>
━━━━━━━━━━━━━━━━━━
📱 <b>Number Searched:</b> {number}
⚠️ <b>Status:</b> Error: {str(e)[:100]}
━━━━━━━━━━━━━━━━━━
<b>Credits Left:</b> {user['credits'] if user_id != ADMIN_ID else 'Unlimited'}
━━━━━━━━━━━━━━━━━━
<b>Powered by @MAGMAxRICH</b>
        """
        send_msg(chat_id, result, reply_to=reply_to)
    
    is_still_member = check_membership(user_id)
    
    if is_still_member:
        credits_msg = f"""
━━━━━━━━━━━━━━━━━━
💰 <b>Your Credits:</b> {user['credits'] if user_id != ADMIN_ID else 'Unlimited'}
        """
        send_msg(chat_id, credits_msg, reply_to=reply_to)
    else:
        warning = f"""
⚠️ <b>MEMBERSHIP LOST!</b>

Please rejoin to continue using the bot.
        """
        send_msg(chat_id, warning, force_join_kb(), reply_to=reply_to)

# ✅ Handle Start Command
def handle_start(user_id, name, args, chat_id=None, reply_to=None):
    chat_id = chat_id or user_id
    
    if not is_group_chat(chat_id) and user_id != ADMIN_ID:
        handle_private_message(user_id, name, "/start", chat_id, reply_to)
        return
    
    is_member = check_membership(user_id)
    
    if not is_member:
        msg = f"""
<b>Welcome {name} to Number Info Bot! 👋</b>
━━━━━━━━━━━━━━━━━━
<b>Powered by @MAGMAxRICH</b>
━━━━━━━━━━━━━━━━━━

🔒 <b>MEMBERSHIP REQUIRED!</b>

To use this bot, you must join:

<b>Support Group:</b> {GROUP}  
<b>Update Channel:</b> {CHANNEL}

<b>Steps:</b>
1️⃣ Click JOIN buttons below
2️⃣ Click VERIFY MEMBERSHIP
3️⃣ Send /start again
        """
        send_msg(chat_id, msg, force_join_kb(), reply_to)
        return
    
    user = get_or_create_user(user_id, name)
    user["membership_verified"] = True
    user["name"] = name
    
    today = str(date.today())
    bonus_msg = ""
    
    if user.get("last_bonus") != today:
        current_credits = user.get("credits", 0)
        if current_credits < 5:
            add_credits = 5 - current_credits
            user["credits"] = 5
            bonus_msg = f"\n🎁 <b>Daily Bonus: {add_credits} credit{'s' if add_credits > 1 else ''} added!</b>"
        else:
            bonus_msg = f"\n📊 <b>You already have {current_credits} credits</b>"
        
        user["last_bonus"] = today
        save_users()
    
    welcome = f"""
<b>Welcome back {name}! 👋</b>{bonus_msg}
━━━━━━━━━━━━━━━━━━
<b>Powered by @MAGMAxRICH</b>
━━━━━━━━━━━━━━━━━━

✅ <b>Membership Verified</b>
━━━━━━━━━━━━━━━━━━
<b>📱 NUMBER INFO</b> - Mobile number search (JSON Format)
<b>🆔 AADHAR INFO</b> - Aadhar number search
<b>👻 SNAPCHAT INFO</b> - Snapchat username search
<b>💰 MY CREDITS</b> - Check balance: {user['credits']}
<b>👥 REFERRAL</b> - Invite friends: {user['referrals']}
<b>🎟️ REDEEM CODE</b> - Redeem codes for credits
━━━━━━━━━━━━━━━━━━

<b>Search Command:</b>
<code>/num [10-digit-number]</code>

<b>Example:</b>
<code>/num 9876543210</code>

<b>Features:</b>
• JSON Format Results
• Easy to Copy-Paste
• Structured Data
• All in One Block
    """
    
    send_msg(chat_id, welcome, main_menu_kb(user_id), reply_to)

# ✅ Handle Private Messages
def handle_private_message(user_id, name, text, chat_id, message_id):
    if user_id == ADMIN_ID:
        if text.startswith("/start"):
            args = []
            if len(text.split()) > 1:
                args = [text.split()[1]]
            handle_start(user_id, name, args, chat_id, message_id)
            return
        elif text.startswith("/num"):
            handle_num_command(user_id, name, text, chat_id, message_id)
            return
        elif text.isdigit() and len(text) >= 10:
            handle_search(user_id, name, text, chat_id, message_id)
            return
    
    msg = f"""
🤖 <b>NUMBER INFO BOT</b>
━━━━━━━━━━━━━━━━━━
<b>Powered by @MAGMAxRICH</b>
━━━━━━━━━━━━━━━━━━

🚫 <b>BOT CAN ONLY BE USED IN GROUP!</b>

Please join group to use all features:

📢 <b>Support Group:</b> {GROUP}
📢 <b>Update Channel:</b> {CHANNEL}

<b>Features Available in Group:</b>
✅ /num - Mobile number search (JSON Format)
✅ Complete data in one block
✅ Easy copy-paste format
    """
    send_msg(chat_id, msg, join_group_only_kb(), message_id)

# Main Bot Function
def main():
    print("="*60)
    print("🤖 NUMBER INFO BOT - JSON FORMAT")
    print("="*60)
    print(f"👥 Support Group: {GROUP}")
    print(f"📢 Update Channel: {CHANNEL}")
    print("="*60)
    print(f"📱 API URL: {API_URL}")
    print("="*60)
    print("✅ Command: /num [number]")
    print("✅ Output: Complete JSON Format")
    print("="*60)
    
    try:
        bot_info = requests.get(f"https://api.telegram.org/bot{TOKEN}/getMe", timeout=5).json()
        if bot_info.get("ok"):
            print(f"✅ Bot connected: @{bot_info['result']['username']}")
        else:
            print("❌ Bot connection failed")
            return
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return
    
    if str(ADMIN_ID) not in users:
        users[str(ADMIN_ID)] = {
            "credits": 999999,
            "referrals": 0,
            "name": "Admin",
            "last_bonus": "",
            "membership_verified": True,
            "joined_date": str(date.today()),
            "redeemed_codes": []
        }
        save_users()
        print("✅ Admin account created")
    
    offset = 0
    
    while True:
        try:
            resp = requests.get(
                f"https://api.telegram.org/bot{TOKEN}/getUpdates",
                params={"offset": offset, "timeout": 30}
            ).json()
            
            if resp.get("ok"):
                for upd in resp["result"]:
                    offset = upd["update_id"] + 1
                    
                    if "message" in upd:
                        msg = upd["message"]
                        uid = msg["from"]["id"]
                        name = msg["from"].get("first_name", "User")
                        chat_id = msg["chat"]["id"]
                        message_id = msg.get("message_id")
                        
                        chat_type = msg["chat"]["type"]
                        is_group = chat_type in ["group", "supergroup"]
                        
                        if "text" in msg:
                            txt = msg["text"]
                            
                            if not is_group and uid != ADMIN_ID:
                                handle_private_message(uid, name, txt, chat_id, message_id)
                                continue
                            
                            if txt.startswith("/start"):
                                args = []
                                if len(txt.split()) > 1:
                                    args = [txt.split()[1]]
                                handle_start(uid, name, args, chat_id, message_id)
                            
                            elif txt.startswith("/num"):
                                handle_num_command(uid, name, txt, chat_id, message_id)
            
            time.sleep(1)
            
        except KeyboardInterrupt:
            print("\n🤖 Bot stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()