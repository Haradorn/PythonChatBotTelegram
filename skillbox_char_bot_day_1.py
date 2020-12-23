# -*- coding: utf-8 -*-
"""Skillbox Char Bot Day 1

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uJsFDkguYjraymLpzBbLZ4PfRHxT60gR
"""

import nltk
import random

# BOT_CONFIG = {
#     "intents": { # Намерения
#         "hello": { # Намерение поздароваться
#             "examples": ["Привет", "Добрый день", "Шалом", "Здравствуйте"],
#             "responses": ["Привет, человек", "Доброго времени суток"]
#         },
#         "bye": {
#             "examples": ["Пока", "Досвидос", "Прощай"],
#             "responses": ["Счастливо", "До свидания", "Если что, возвращайтесь"],
#         },
#         "howdoyoudo": {
#             "examples": ["Как дела", "Что делаешь", "Какие дела"],
#             "responses": ["Маюсь фигней", "Отвечаю на дурацкие вопросы", "Веду вебинары"],
#         },
#     },
#     "failure_phrases": [
#         "Я ничо не понил",
#         "Что-то непонятно",
#         "Я всего лишь бот, сформулируйте попроще"
#     ]
# }

def filter(text):
  text = text.lower()
  text = [c for c in text if c in 'абвгджзеёийклмнопрстуфхцчшщьыъэюя -']
  return ''.join(text)

def match(text, example): # "прощяй!" === "Прощай" ??
  text = filter(text)
  #example = example
  
  distance = nltk.edit_distance(text, example) / len(example)
  if distance < 0.4:
    return True # Текст совпадает
  else:
    return False # Текст НЕ совпадает

def get_intent(text): 
  for intent, data in BOT_CONFIG['intents'].items():
    for example in data['examples']:
      if match(text, example):
        return intent

def get_answer_by_intent(intent):
  phrases = BOT_CONFIG['intents'][intent]['responses']
  return random.choice(phrases)

def bot(text):
  intent = get_intent(text)

  if not intent:
    intent = get_intent_predictive_model(text)

  print("Intent = ", intent)

  if intent:
    return get_answer_by_intent(intent)

  failure_phrases = BOT_CONFIG['failure_phrases']
  return random.choice(failure_phrases)

question = ''
while question not in ['выход', 'отстань']:
  question = input()
  answer = bot(question)
  print(answer)

import json

config_file = open("/content/big_bot_config.json", "r")

BOT_CONFIG = json.load(config_file)

len(BOT_CONFIG["intents"])

"""Задача: классифицировать намерения пользователя, т.е. на основе фразы спрогнозировать "интент"

Фразы => Намерение
Х(вход) => Y(выходные)
1. Модель (алгоритм) М.О. = Классификатор (Classifier)
2. Преобразование данных (Векторайзер) Vectorizer
Задача Vectorizer это из текста сделать числа (какие-то и как-то)
"""

X_examples = []
y = []
for intent, data in BOT_CONFIG['intents'].items():
  for example in data['examples']:
    X_examples.append(example)
    y.append(intent)

from sklearn.feature_extraction.text import CountVectorizer

count_vecrorizer = CountVectorizer()
count_vecrorizer.fit(X_examples)

# list(count_vecrorizer.transform(['ты там че делаешь то']).nonzero()[1])

X = count_vecrorizer.transform(X_examples)

from sklearn.linear_model import LogisticRegression

log_reg = LogisticRegression() #Настройки
log_reg.fit(X, y)

log_reg.predict(count_vecrorizer.transform(['ну расскажи анекдот']))

log_reg.score(X, y)

from sklearn.svm import LinearSVC

from sklearn.feature_extraction.text import TfidfVectorizer
tfidf_vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(2,4))
X = tfidf_vectorizer.fit_transform(X_examples)

from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size = 0.33
)

lin_svc = LinearSVC()
lin_svc.fit(X_train, y_train)
print("Train", lin_svc.score(X_train, y_train))
print("Test", lin_svc.score(X_test, y_test))

def get_intent_predictive_model(text):
  return lin_svc.predict(tfidf_vectorizer.transform([text]))[0]

import pickle

pickle.dump(lin_svc, open("lin_svc.model", "wb"))
pickle.dump(tfidf_vectorizer, open("tfidf_vectorizer.model", "wb"))

! pip install python-telegram-bot --upgrade

from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

def start(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hi!')


def help_command(update: Update, context: CallbackContext) -> None:
    """Send a message when the command /help is issued."""
    update.message.reply_text('I\'m very intelligent AI creature!')


def echo(update: Update, context: CallbackContext) -> None:
    """Echo the user message."""
    answer = bot(update.message.text)
    update.message.reply_text(answer)


def main():
    """Start the bot."""
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater("1474068577:AAEOuQoOn5p5bTPHeN3NMu74qT7MVmyhq-w", use_context=True)

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    # on different commands - answer in Telegram
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    # on noncommand i.e message - echo the message on Telegram
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

main()

