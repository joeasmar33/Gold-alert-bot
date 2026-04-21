import os
import time
import json
import requests
import datetime
import google.generativeai as genai

TELEGRAM_TOKEN = '8778410174:AAHgOSO9R9DPtOlCNazB_eaUM3CdsYE5EJk'
TELEGRAM_CHAT_ID = '1344418276'
GEMINI_API_KEY = 'AIzaSyAAYe7oOIZulmsM4_uT2FUPG_x8YVaqBhQ'
SCAN_INTERVAL = 60

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')
sent_headlines = set()

def send_telegram(message):
    url = 'https://api.telegram.org/bot' + TELEGRAM_TOKEN + '/sendMessage'
    payload = {'chat_id': TELEGRAM_CHAT_ID, 'text': message, 'parse_mode': 'HTML'}
    try:
        r = requests.post(url, json=payload, timeout=10)
        return r.status_code == 200
    except Exception as e:
        print(str(e))
        return False

def scan_gold_news():
    now = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    prompt = 'Search for breaking news in the last 30 minutes affecting XAU/USD gold prices. Focus on Trump statements, Fed decisions, tariffs, wars, inflation data. Return ONLY a valid JSON array, no markdown, like: [{"headline":"text","source":"name","impact":"HIGH or MEDIUM or LOW","direction":"UP or DOWN","estimated_move":"+$15","reason":"one sentence"}]. If nothing found return []'
    try:
        response = model.generate_content(prompt)
        text = response.text.strip().replace('```json','').replace('```','').strip()
        start = text.find('[')
        end = text.rfind(']') + 1
        if start == -1:
            return []
        return json.loads(text[start:end])
    except Exception as e:
        print(str(e))
        return []

def run():
    print('Gold Alert Bot started')
    send_telegram('<b>GOLD SIGNAL BOT ACTIVATED</b>\n\nScanning 24/7 for:\n- Trump statements\n- Fed decisions\n- Tariffs and trade wars\n- Geopolitical conflicts\n- Inflation data\n\nAlerts coming instantly!')
    while True:
        try:
            items = scan_gold_news()
            for item in items:
                headline = item.get('headline','')
                impact = item.get('impact','LOW')
                if headline in sent_headlines:
                    continue
                if impact in ['HIGH','MEDIUM']:
                    direction = item.get('direction','')
                    move = item.get('estimated_move','')
                    reason = item.get('reason','')
                    source = item.get('source','')
                    msg = '<b>GOLD ALERT - ' + impact + '</b>\n\n' + headline + '\n\nSource: ' + source + '\nDirection: ' + direction + '\nMove: ' + move + '\nWhy: ' + reason
                    if send_telegram(msg):
                        sent_headlines.add(headline)
                        if len(sent_headlines) > 200:
                            sent_headlines.clear()
        except Exception as e:
            print(str(e))
        time.sleep(SCAN_INTERVAL)

if __name__ == '__main__':
    run()
