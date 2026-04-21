import os
import time
import json
import requests
import datetime
import google.generativeai as genai

# ─── CONFIG ─────────────────────────────────────────────────

TELEGRAM_TOKEN = “8778410174:AAHgOSO9R9DPtOlCNazB_eaUM3CdsYE5EJk”
TELEGRAM_CHAT_ID = “1344418276”
GEMINI_API_KEY = “AIzaSyAAYe7oOIZulmsM4_uT2FUPG_x8YVaqBhQ”
SCAN_INTERVAL = 60  # seconds between scans

# ────────────────────────────────────────────────────────────

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(“gemini-2.0-flash”)

sent_headlines = set()  # avoid duplicate alerts

def send_telegram(message):
url = f”https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage”
payload = {
“chat_id”: TELEGRAM_CHAT_ID,
“text”: message,
“parse_mode”: “HTML”
}
try:
r = requests.post(url, json=payload, timeout=10)
return r.status_code == 200
except Exception as e:
print(f”Telegram error: {e}”)
return False

def scan_gold_news():
now = datetime.datetime.utcnow().strftime(”%Y-%m-%d %H:%M UTC”)
prompt = f”””
You are a gold market intelligence scanner. Current time: {now}

Search the web RIGHT NOW for breaking news in the last 30 minutes that could move XAU/USD gold prices.

Focus ONLY on:

- Trump statements, tweets, Truth Social posts about tariffs, Fed, dollar, trade
- Federal Reserve / Powell statements or decisions
- Geopolitical conflicts, war escalations, sanctions
- Inflation data, CPI, jobs reports surprises
- Bank failures or financial crises
- Major currency moves (USD weakness/strength)
- Central bank gold buying

Return ONLY a valid JSON array. No markdown. No explanation. Just JSON.
Format:
[
{{
“headline”: “full headline here”,
“source”: “source name”,
“impact”: “HIGH or MEDIUM or LOW”,
“direction”: “UP or DOWN or UNCERTAIN”,
“estimated_move”: “+$15 to +$25”,
“reason”: “one sentence why this moves gold”
}}
]

If NO relevant breaking news found in last 30 minutes, return empty array: []
“””
try:
response = model.generate_content(prompt)
text = response.text.strip()
# Clean markdown if present
text = text.replace(”`json", "").replace("`”, “”).strip()
# Find JSON array
start = text.find(”[”)
end = text.rfind(”]”) + 1
if start == -1:
return []
json_str = text[start:end]
return json.loads(json_str)
except Exception as e:
print(f”Gemini error: {e}”)
return []

def format_alert(item):
impact = item.get(“impact”, “UNKNOWN”)
direction = item.get(“direction”, “UNCERTAIN”)
headline = item.get(“headline”, “”)
source = item.get(“source”, “Unknown”)
move = item.get(“estimated_move”, “Unknown”)
reason = item.get(“reason”, “”)

```
if impact == "HIGH":
    emoji = "🚨🔴"
elif impact == "MEDIUM":
    emoji = "⚠️🟡"
else:
    emoji = "ℹ️🔵"

dir_emoji = "📈" if direction == "UP" else "📉" if direction == "DOWN" else "↔️"
now = datetime.datetime.utcnow().strftime("%H:%M UTC")

msg = f"""{emoji} <b>GOLD ALERT — {impact} IMPACT</b>
```

📰 <b>{headline}</b>

🏦 Source: {source}
{dir_emoji} Direction: <b>XAU/USD {direction}</b>
💰 Est. Move: <b>{move}</b>
🧠 Why: {reason}

⏰ {now}
━━━━━━━━━━━━━━━━━━━━
<i>GoldSignal Bot — XAU/USD Intelligence</i>”””
return msg

def run():
print(“🚀 Gold Alert Bot started…”)
send_telegram(””“🟢 <b>GOLD SIGNAL BOT ACTIVATED</b>

I’m now scanning 24/7 for breaking news that affects XAU/USD:

✅ Trump statements & Truth Social
✅ Federal Reserve decisions
✅ Tariffs & trade wars  
✅ Geopolitical conflicts
✅ Inflation & economic data
✅ USD major moves

You’ll be notified INSTANTLY for HIGH & MEDIUM impact events.

⏱ Scanning every 60 seconds…”””)

```
while True:
    print(f"[{datetime.datetime.utcnow().strftime('%H:%M:%S')}] Scanning...")
    try:
        news_items = scan_gold_news()

        if not news_items:
            print("  → No breaking news found")
        else:
            for item in news_items:
                headline = item.get("headline", "")
                impact = item.get("impact", "LOW")

                # Skip duplicates
                if headline in sent_headlines:
                    continue

                # Only alert HIGH and MEDIUM
                if impact in ["HIGH", "MEDIUM"]:
                    msg = format_alert(item)
                    success = send_telegram(msg)
                    if success:
                        sent_headlines.add(headline)
                        print(f"  → ALERT SENT: {headline[:60]}...")
                    # Keep set manageable
                    if len(sent_headlines) > 200:
                        sent_headlines.clear()
                else:
                    print(f"  → LOW impact, skipped: {headline[:60]}")

    except Exception as e:
        print(f"  → Error: {e}")

    time.sleep(SCAN_INTERVAL)
```

if **name** == “**main**”:
run()
