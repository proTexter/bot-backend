import requests
import json
import pickle
import random
import re
import nltk
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
import shelve

data = shelve.open("data")

import re
class TextNormalizer():
    def __init__(self, language = 'english'):
        self.stopwors = stopwords.words(language)
        self.stemmer = PorterStemmer()
        self.vocabulary = json.load(open('vocabulary.json', 'r'))
        print(self.vocabulary)
    def transform(self, X):
        for i in range(len(X)):
            X[i] = X[i].replace('\n', ' ')
            X[i] = X[i].replace('\r', ' ')
            X[i] = re.sub('[^\x00-\x7F]+', '', X[i])
            X[i] = X[i].lower()
            X[i] = ' '.join(re.findall('[a-zA-Z]+', X[i]))
            X[i] = ' '.join([word for word in X[i].split() if len(word) >= 2])
            X[i] = ' '.join([word for word in X[i].split() if not word in self.stopwors])
            X[i] = ' '.join([self.stemmer.stem(word) for word in X[i].split()])
            X[i] = ' '.join([word for word in X[i].split() if word in self.vocabulary])
        return X

norm = pickle.load(open('normalizer.obj', 'rb'))
vectorizer = pickle.load(open('vectorizer.obj', 'rb'))
svc = pickle.load(open('model.obj', 'rb'))


greetings = ["Hi"]
bye = ['Bye', 'Bye-Bye', 'Goodbye', 'Have a good day','Stop']
thank_you = ['Thanks', 'Thank you', 'Thanks a bunch', 'Thanks a lot.', 'Thank you very much', 'Thanks so much', 'Thank you so much']
thank_response = ['You\'re welcome.' , 'No problem.', 'No worries.', ' My pleasure.' , 'It was the least I could do.', 'Glad to help.']
# Example of how bot match the keyword from Greetings and reply accordingly
def bot_initialize(user_msg):
    if(user_msg in greetings):
          return random.choice(greetings)
    elif(user_msg in thank_you):
          return random.choice(thank_response)

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
            return f"Dear {name} - you have 2 chances more", 1


def bot_initialize(user_msg, chat_di, user_id, name):
    flag=True
    while(flag==True):
        user_response = user_msg
        if(user_response not in bye):
            if(user_response == '/start'):
                bot_resp = """Hi! There. I am your Corona Protector. I can tell you all the Facts and Figures, Signs and Symptoms related to spread of Covid-19 in India. \nType Bye to Exit."""
                return bot_resp
            elif(user_response in thank_you):
                bot_resp = random.choice(thank_response)
                return bot_resp
            elif(user_response in greetings):
                bot_resp = random.choice(greetings) + ", What information you what related to Covid-19 in India"
                return bot_resp
            else:
                user_response = user_response.lower()
                bot_resp, status = response(user_response, chat_id, user_id, name)
                if status == -1:
                    tbot.
                #sent_tokens.remove(user_response)   # remove user question from sent_token that we added in sent_token in response() to find the Tf-Idf and cosine_similarity
                return bot_resp
        else:
            flag = False
            bot_resp = random.choice(bye)
            return bot_resp

class telegram_bot():
    def __init__(self):
        self.token = '1461365521:AAFRkkYbl76cm9EcVkMBn5peEtWL7cf_Y44'
        self.url = f"https://api.telegram.org/bot{self.token}"

    def get_updates(self, offset=None):
        url = self.url + "/getUpdates?timeout=100"
        if offset:
            url = url + f"&offset={offset+1}"
        url_info = requests.get(url)
        return json.loads(url_info.content)

    def cickUser(self, chat_id, user_id):

    def send_message(self, msg, chat_id):
        url = self.url + f'/sendMessage?chat_id={chat_id}&text={msg}'
        if msg is not None:
            requests.get(url)

tbot = telegram_bot()
update_id = None

def make_reply(msg, chat_id, user_id, name):
    if msg is not None:
        reply = bot_initialize(msg, chat_id, user_id, name)
    else:
        return ''
    return reply

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
            #from_ = item['message']['from']['id']
            #print(from_)
        reply = make_reply(message, chat_id, user_id, name)
        tbot.send_message(reply, chat_id)