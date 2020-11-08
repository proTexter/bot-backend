import json
import pickle
import random
import re
import requests
import shelve

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

data = shelve.open("data")

class TextNormalizer:

    def __init__(self, language='english'):
        self.stop_words = stopwords.words(language)
        self.stemmer = PorterStemmer()
        self.vocabulary = json.load(open('vocabulary.json', 'r'))
        print(self.vocabulary)

    def transform(self, x):
        for i in range(len(x)):
            x[i] = x[i].replace('\n', ' ')
            x[i] = x[i].replace('\r', ' ')
            x[i] = re.sub('[^\x00-\x7F]+', '', x[i])
            x[i] = x[i].lower()
            x[i] = ' '.join(re.findall('[a-zA-Z]+', x[i]))
            x[i] = ' '.join([word for word in x[i].split() if len(word) >= 2])
            x[i] = ' '.join([word for word in x[i].split() if not word in self.stop_words])
            x[i] = ' '.join([self.stemmer.stem(word) for word in x[i].split()])
            x[i] = ' '.join([word for word in x[i].split() if word in self.vocabulary])
        return x


norm = TextNormalizer()#pickle.load(open('normalizer.obj', 'rb'))
svc = pickle.load(open('model.obj', 'rb'))
vectorizer = pickle.load(open('vectorizer.obj', 'rb'))

greetings = ["Hi"]
farewells = ['Bye', 'Bye-Bye', 'Goodbye', 'Have a good day', 'Stop']
thank_you = ['Thanks', 'Thank you', 'Thanks a bunch', 'Thanks a lot.', 'Thank you very much', 'Thanks so much',
             'Thank you so much']
thank_response = ['You\'re welcome.', 'No problem.', 'No worries.', ' My pleasure.', 'It was the least I could do.',
                  'Glad to help.']


def bot_initialize(user_msg, chat_id, user_id, name):
    flag = True
    while flag:
        user_response = user_msg
        if user_response not in farewells:
            if user_response == '/start':
                bot_resp = """Hi! There. I am proTexter. \nI'll keep the bad guys out. \nType Bye to Exit."""
                return bot_resp
            elif user_response in thank_you:
                bot_resp = random.choice(thank_response)
                return bot_resp
            elif user_response in greetings:
                bot_resp = random.choice(greetings)
                return bot_resp
            else:
                user_response = user_response.lower()
                bot_resp = response(user_response, chat_id, user_id, name)
                print(bot_resp)
                (bot_resp, status) = bot_resp
                if status == -1:
                    tbot.kick_user(chat_id, user_id)
                return bot_resp
        else:
            flag = False
            bot_resp = random.choice(farewells)
            return bot_resp


def response(user_response, chat_id, user_id, name):
    normed_text = norm.transform([user_response])
    vector = vectorizer.transform(normed_text)
    res = svc.predict(vector)
    if res[0] == 1:
        if f"{chat_id}|{user_id}" in data:
            if data[f"{chat_id}|{user_id}"] == 1:
                return f"Dear {name} - you are banned", -1
            else:
                data[f"{chat_id}|{user_id}"] -= 1
                return f"Dear {name} - if you will send {data[f'{chat_id}|{user_id}']} more messages like this you will be banned", 1
        else:
            data[f"{chat_id}|{user_id}"] = 3
            return f"Dear {name} - you have 2 more chances", 1
    else:
        return "", 1


class telegram_bot():
    def __init__(self):
        self.token = '1461365521:AAFRkkYbl76cm9EcVkMBn5peEtWL7cf_Y44'
        self.url = f"https://api.telegram.org/bot{self.token}"

    def get_updates(self, offset=None):
        url = self.url + "/getUpdates?timeout=100"
        if offset:
            url = url + f"&offset={offset + 1}"
        url_info = requests.get(url)
        return json.loads(url_info.content)

    def send_message(self, msg, chat_id):
        url = self.url + f'/sendMessage?chat_id={chat_id}&text={msg}'
        if msg is not None:
            requests.get(url)

    def kick_user(self, chat_id, user_id):
        url = self.url + f'/kickChatMember?chat_id={chat_id}&user_id={user_id}'
        requests.get(url)


def make_reply(msg, chat_id, user_id, name):
    if msg is not None:
        reply = bot_initialize(msg, chat_id, user_id, name)
    else:
        return ''
    return reply


tbot = telegram_bot()
update_id = None
textNormalizer = TextNormalizer()

while True:
    print('...')
    updates = tbot.get_updates(offset=update_id)
    updates = updates['result']
    print(updates)
    if updates:
        for item in updates:
            update_id = item['update_id']
            try:
                message = item['message']['text']
                print(message)
            except:
                message = None
            chat_id = item['message']['chat']['id']
            user_id = item['message']['from']['id']
            name = item['message']['from']['username']

        reply = make_reply(message, chat_id, user_id, name)
        tbot.send_message(reply, chat_id)
