import telebot
import requests
import json

from telebot import types

Bot = telebot.TeleBot("token")

keys = {
    "рубль": "RUB",
    "доллар": "USD",
    "евро": "EUR"
}


class ConvertionException(Exception):
    pass


class CryptoConverter:
    @staticmethod
    def convert(quote: str, base: str, ammount: str):
        if quote == base:
            raise ConvertionException(f"Невозможно конвертировать одинаковые валюты {base}")
        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise ConvertionException(f"Не удалось обработать валюту {quote}")
        try:
            base_ticker = keys[base]
        except KeyError:
            raise ConvertionException(f"Не удалось обработать валюту {base}")
        try:
            ammount = float(ammount)
        except ValueError:
            raise ConvertionException(f"Не удалось обработать количество {ammount}")
        r = requests.get(
            f"https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}&api_key=10202fea6bdfa93e2601bba654c10767b15834e3c4bcf2c5a9bb12e6dfbbb547")
        total_base = json.loads(r.content)[keys[base]]*ammount

        return total_base


@Bot.message_handler(commands=["start"])
def start(message):
    greet = f"Здравствуйте, <b>{message.from_user.first_name} {message.from_user.last_name}</b>"
    greet_1 = f"Нажмите /info для начала работы"
    Bot.send_message(message.chat.id, greet, parse_mode="html")
    Bot.send_message(message.chat.id, greet_1)


@Bot.message_handler(commands=["info"])
def info(message):
    markup = types.InlineKeyboardMarkup(row_width=2)
    description = types.InlineKeyboardButton(text="Описание", callback_data="question_1")
    information = types.InlineKeyboardButton(text="Принцип работы", callback_data="question_2")
    markup.add(description, information)
    Bot.send_message(message.chat.id, "Выберите опцию", reply_markup=markup)


@Bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.message:
        if call.data == "question_1":
            Bot.send_message(call.message.chat.id,
                             "Бот предназначен для получения стоимости валюты и конвертации валют")
            Bot.send_message(call.message.chat.id, "Доступные валюты: рубль (RUB), доллар (USD), евро (EUR)")
        elif call.data == "question_2":
            Bot.send_message(call.message.chat.id, "Введите <валюта №1> <валюта №2> <количество валюты №1>")
            Bot.send_message(call.message.chat.id, '''Например, "рубль евро 1"''')


@Bot.message_handler(content_types=["text", ])
def converter(message: telebot.types.Message):
    try:
        values = message.text.split(' ')
        if len(values) != 3:
            raise ConvertionException("Слишком много запросов")
        quote, base, ammount = values
        total_base = CryptoConverter.convert(quote, base, ammount)
    except ConvertionException as e:
        Bot.reply_to(message, f"Ошибка пользователя\n{e}")
    except Exception as e:
        Bot.reply_to(message, f"Не удалось обработать команду\n{e}")
    else:
        text = f"Цена {ammount} {quote} в {base} - {total_base}"
        Bot.send_message(message.chat.id, text)


Bot.polling(none_stop=True)
