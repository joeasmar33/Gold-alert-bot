import time
import requests
import datetime
import xml.etree.ElementTree as ET

TELEGRAM_TOKEN = '8778410174:AAHgOSO9R9DPtOlCNazB_eaUM3CdsYE5EJk'
TELEGRAM_CHAT_ID = '1344418276'
SCAN_INTERVAL = 120

sent_headlines = set()

GOLD_KEYWORDS = [
    'trump','tariff','tariffs','federal reserve','fed rate',
    'powell','rate cut','rate hike','inflation','gold price',
    'xauusd','war','sanctions','geopolit','dollar index',
    'recession','bank fail','debt ceiling','china trade',
    'iran','ukraine','russia','safe haven','bullion'
]

RSS_FEEDS = [
    'https://feeds.reuters.com/reuters/businessNews',
    'https://feeds.reuters.com/reuters/topNews',
    'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=100003114',
    'https://feeds.marketwatch.com/marketwatch/topstories',
]

def send_telegram(message):
    url = 'https://api.telegram.org/bot' + TELEGRAM_TOKEN + '/sendMessage'
    try:
        requests.post(url, json={
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message,
            'parse_mode': 'HTML'
        }, timeout=10)
    except Exception as e:
        print(str(e))

def fetch_rss(url):
    try:
        r = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        root = ET.fromstring(r.content)
        items = []
        for item in root.iter('item'):
            title = item.findtext('title') or ''
            desc = item.findtext('description') or ''
            link = item.findtext('link') or ''
            items.append({'title': title, 'desc': desc, 'link': link})
        return items
    except Exception as e:
        print(str(e))
        return []

def is_gold_relevant(text):
    text_lower = text.lower()
    for kw in GOLD_KEYWORDS:
        if kw in text_lower:
            return kw
    return None

def estimate_impact(text):
    text_lower = text.lower()
    high = ['trump','tariff','war','sanctions','fed rate','rate cut','rate hike','bank fail','debt ceiling']
    for h in high:
        if h in text_lower:
            return 'HIGH'
    return 'MEDIUM'

def estimate_direction(text):
    text_lower = text.lower()
    up_words = ['tariff','war','sanction','inflation','weak dollar','rate cut','crisis','fail','conflict','safe haven']
    down_words = ['rate hike','strong dollar','ceasefire','peace','recovery','beat expectations']
    for w in up_words:
        if w in text_lower:
            return 'UP'
    for w in down_words:
        if w in text_lower:
            return 'DOWN'
    return 'UNCERTAIN'

def run():
    print('Gold Alert Bot started - using RSS feeds')
    send_telegram('<b>GOLD SIGNAL BOT ACTIVATED</b>\n\nNow scanning Reuters, CNBC, MarketWatch every 2 minutes for:\n- Trump statements\n- Fed decisions\n- Tariffs and wars\n- Inflation data\n- Geopolitical events\n\nAlerts incoming instantly!')

    while True:
        print('Scanning RSS feeds...')
        for feed_url in RSS_FEEDS:
            items = fetch_rss(feed_url)
            for item in items:
                title = item['title']
                desc = item['desc']
                full_text = title + ' ' + desc
                keyword = is_gold_relevant(full_text)
                if not keyword:
                    continue
                if title in sent_headlines:
                    continue
                impact = estimate_impact(full_text)
                direction = estimate_direction(full_text)
                dir_emoji = 'GOLD UP' if direction == 'UP' else 'GOLD DOWN' if direction == 'DOWN' else 'WATCH'
                now = datetime.datetime.utcnow().strftime('%H:%M UTC')
                msg = (
                    '<b>GOLD ALERT - ' + impact + '</b>\n\n'
                    + title + '\n\n'
                    + 'Signal: ' + dir_emoji + '\n'
                    + 'Trigger: ' + keyword.upper() + '\n'
                    + 'Time: ' + now
                )
                send_telegram(msg)
                sent_headlines.add(title)
                print('Alert sent: ' + title[:60])
                if len(sent_headlines) > 500:
                    sent_headlines.clear()
        time.sleep(SCAN_INTERVAL)

if __name__ == '__main__':
    run()
