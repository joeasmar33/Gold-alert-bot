
import time
import requests
import datetime
import xml.etree.ElementTree as ET

TELEGRAM_TOKEN = '8778410174:AAHgOSO9R9DPtOlCNazB_eaUM3CdsYE5EJk'
TELEGRAM_CHAT_ID = '1344418276'
SCAN_INTERVAL = 120

sent_headlines = set()

GOLD_KEYWORDS = [
    'trump tariff', 'trump tax', 'trump sanction', 'trump fed',
    'trump dollar', 'trump trade', 'trump china', 'trump iran',
    'federal reserve rate', 'fed rate cut', 'fed rate hike',
    'powell rate', 'interest rate decision', 'rate decision',
    'gold price', 'gold surges', 'gold falls', 'gold jumps',
    'xauusd', 'gold futures', 'spot gold',
    'military strike', 'missile attack', 'war declared',
    'troops deployed', 'nuclear threat', 'ceasefire',
    'iran sanction', 'russia sanction', 'china sanction',
    'oil embargo', 'trade war', 'trade deal',
    'inflation rate', 'cpi data', 'cpi report',
    'bank collapse', 'bank failure', 'bank run',
    'debt ceiling', 'us default', 'dollar collapse',
    'dollar index falls', 'dollar weakens',
    'safe haven demand', 'flight to safety',
    'geopolitical tension', 'geopolitical crisis',
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

def estimate_impact(keyword):
    high = [
        'trump tariff', 'trump sanction', 'federal reserve rate',
        'fed rate cut', 'fed rate hike', 'powell rate',
        'military strike', 'missile attack', 'war declared',
        'nuclear threat', 'bank collapse', 'bank failure',
        'debt ceiling', 'us default', 'gold surges', 'gold jumps',
        'iran sanction', 'trade war', 'dollar collapse'
    ]
    for h in high:
        if h in keyword:
            return 'HIGH'
    return 'MEDIUM'

def estimate_direction(text):
    text_lower = text.lower()
    up_words = [
        'tariff', 'strike', 'sanction', 'inflation', 'rate cut',
        'crisis', 'collapse', 'fail', 'conflict', 'safe haven',
        'tension', 'nuclear', 'weakens', 'falls', 'embargo'
    ]
    down_words = [
        'rate hike', 'strong dollar', 'ceasefire', 'peace deal',
        'recovery', 'beat expectations', 'trade deal signed'
    ]
    for w in down_words:
        if w in text_lower:
            return 'DOWN'
    for w in up_words:
        if w in text_lower:
            return 'UP'
    return 'WATCH'

def run():
    print('Gold Alert Bot started')
    send_telegram(
        '<b>GOLD SIGNAL BOT ACTIVATED</b>\n\n'
        'Scanning Reuters, CNBC, MarketWatch every 2 min for:\n'
        '- Trump tariffs and statements\n'
        '- Fed rate decisions\n'
        '- Military strikes and wars\n'
        '- Inflation and CPI data\n'
        '- Bank failures and crises\n\n'
        'Only HIGH impact gold news will alert you!'
    )
    while True:
        print('Scanning...')
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
                impact = estimate_impact(keyword)
                direction = estimate_direction(full_text)
                dir_emoji = '📈 GOLD UP' if direction == 'UP' else '📉 GOLD DOWN' if direction == 'DOWN' else '👀 WATCH'
                now = datetime.datetime.utcnow().strftime('%H:%M UTC')
                msg = (
                    '<b>⚡ GOLD ALERT - ' + impact + '</b>\n\n'
                    + '📰 ' + title + '\n\n'
                    + dir_emoji + '\n'
                    + '🔑 Trigger: ' + keyword.upper() + '\n'
                    + '⏰ ' + now
                )
                send_telegram(msg)
                sent_headlines.add(title)
                print('Sent: ' + title[:60])
                if len(sent_headlines) > 500:
                    sent_headlines.clear()
        time.sleep(SCAN_INTERVAL)

if __name__ == '__main__':
    run()
