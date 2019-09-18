# coding: utf8
import telebot
from telebot import apihelper, types
from configparser import ConfigParser
from strings2 import *
from lxml.html import fromstring as fs
from requests import get
from json import loads

cfg = ConfigParser()
cfg.read('config.ini')

cities_list = 'Бендеры,Тирасполь,Григориополь,Днестровск,Дубоссары,Каменка,Рыбница,Слободзея,Новотираспольский'

# apihelper.proxy = {
#     'https': 'https://{}:{}'.format(cfg['Bot']['host'], cfg['Bot']['port'])}
bot = telebot.TeleBot(cfg['Bot']['token'])

cities = {}
stage = {}
search_results = {}


def make_city_keyboard():
    markup = types.ReplyKeyboardMarkup()
    c = cities_list.split(',')
    buttons = [types.KeyboardButton(x) for x in c]
    markup.row(*buttons[:3])
    markup.row(*buttons[3:6])
    markup.row(*buttons[6:])
    return markup


@bot.message_handler(commands=['start', 'help'])
def start(msg):
    if not cities.get(msg.chat.id):
        bot.send_message(msg.chat.id, hello_1)
        bot.send_message(msg.chat.id, hello_2)
        bot.send_message(msg.chat.id, ask_cities,
                         reply_markup=make_city_keyboard())
    else:
        bot.send_message(msg.chat.id, hello_3,
                         reply_markup=types.ReplyKeyboardRemove())
        stage[msg.chat.id] = 'search'


@bot.message_handler(func=lambda x: x.chat.id not in cities)
def write_city(msg):
    cities[msg.chat.id] = msg.text
    start(msg)


@bot.message_handler(func=lambda x: stage.get(x.chat.id) == 'search')
def search(msg):
    suggestions = get(cfg['eapteka']['base'].format(
        msg.text)).json()['suggestions']
    s = select_number + '\n\n'
    for pair in enumerate(suggestions, 1):
        s += "{}) {}\n".format(*pair)
    bot.send_message(msg.chat.id, s)
    search_results[msg.chat.id] = suggestions
    stage[msg.chat.id] = 'show_info'


@bot.message_handler(func=lambda x: x.text.strip().isdigit() and stage[x.chat.id] == 'show_info' and 0 < int(x.text) <= len(search_results[x.chat.id]))
def show_info(msg):
    page = fs(get(cfg['eapteka']['info'].format(
        search_results[msg.chat.id][int(msg.text) - 1], cities[msg.chat.id] if cities[msg.chat.id] in cfg['eapteka']['cities'].split(',') else all_cities)).text)
    places = page.xpath('//table[@id="spravka"]//tr/td[5]/a/text()')
    prices = page.xpath('//table[@id="spravka"]//tr/td[4]/text()')
    s = search_results_text.format(
        search_results[msg.chat.id][int(msg.text) - 1])
    for pair in zip(places, prices):
        s += '{:75} {}\n'.format(pair[0].strip(), pair[1].strip())
    bot.send_message(msg.chat.id, s)
    bot.send_message(msg.chat.id, hello_3)
    stage[msg.chat.id] = 'search'


@bot.message_handler(func=lambda x: True)
def else_(msg):
    bot.send_message(msg.chat.id, not_resolved)


bot.polling()
