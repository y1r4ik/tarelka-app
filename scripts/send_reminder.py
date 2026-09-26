#!/usr/bin/env python3
import json, os, sys, urllib.request, urllib.error, datetime

TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
if not TOKEN:
    print('TELEGRAM_BOT_TOKEN не задан.', file=sys.stderr)
    sys.exit(1)

MESSAGES = [
    'Добрый вечер! 🍽 Загляните в «Тарелку» и спланируйте меню на завтра.',
    'Проверьте список покупок в «Тарелке» — может, чего-то не хватает на неделю?',
    'Новый день — новое меню! Откройте «Тарелку» и выберите, что приготовить.',
    'Не забудьте отметить, что уже есть дома — список покупок обновится сам.',
    'Пара минут на планирование сейчас — и меньше хлопот с готовкой вечером. Откройте «Тарелку».',
]
APP_URL = 'https://t.me/TarelkaRus_bot/menu'

def load_chat_ids(path='chat_ids.json'):
    with open(path, encoding='utf-8') as f:
        return json.load(f)

def send(chat_id, text):
    url = 'https://api.telegram.org/bot' + TOKEN + '/sendMessage'
    payload = {'chat_id': chat_id, 'text': text,
        'reply_markup': {'inline_keyboard': [[{'text': 'Открыть Тарелку', 'url': APP_URL}]]}}
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print('chat_id=' + str(chat_id) + ': OK ' + resp.read().decode('utf-8')[:200])
    except urllib.error.HTTPError as e:
        print('chat_id=' + str(chat_id) + ': HTTP ' + str(e.code) + ' ' + e.read().decode('utf-8')[:300], file=sys.stderr)
    except Exception as e:
        print('chat_id=' + str(chat_id) + ': ERROR ' + str(e), file=sys.stderr)

def main():
    chat_ids = load_chat_ids()
    if not chat_ids:
        print('chat_ids.json пуст — добавьте хотя бы один chat_id.')
        return
    day = datetime.date.today().toordinal()
    text = MESSAGES[day % len(MESSAGES)]
    for cid in chat_ids:
        send(cid, text)

if __name__ == '__main__':
    main()
