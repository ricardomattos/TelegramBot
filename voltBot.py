import os
import json
import redis
import requests
from time import strftime

BOT_TOKEN = os.environ("<token>")
BOT_URL = "https://api.telegram.org/bot{}/".format(BOT_TOKEN)
DEFAULT_TIMEOUT = 60  # seconds
BOT_UPDATES_URL = BOT_URL + "getUpdates?timeout={}".format(DEFAULT_TIMEOUT)
BOT_UPDATES_OFFSET = "offset"

# used to storage the last update_id received
cache = redis.StrictRedis(host="localhost", port=6379, db=0)


def make_request(url):
    response = requests.get(url)
    content = response.content.decode("utf-8")
    return json.loads(content)


def get_updates(url):
    print("Checking updates %s" % strftime("%H:%M:%S"))
    content = make_request(url + "&offset={}".format(cache.get(BOT_UPDATES_OFFSET)))
    return content


def get_messages(update_result):
    chat_update_id = []
    for msg in update_result["result"]:
        chat_id = msg["message"]["chat"]["id"]
        chat_message = msg["message"]["text"]
        chat_update_id.append(msg["update_id"])
        cache.set(BOT_UPDATES_OFFSET, max(chat_update_id) + 1)
        yield chat_id, chat_message


def send_message(chat_id, text):
    url = BOT_URL + "sendMessage?chat_id={}&text={}&parse_mode=HTML".format(
        chat_id, str(text)
    )
    make_request(url)


if __name__ == "__main__":
    while True:
        for chat_id, text in get_messages(get_updates(BOT_UPDATES_URL)):
            send_message(chat_id, text)
