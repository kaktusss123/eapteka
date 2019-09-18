# coding: utf8
import telebot
from telebot import apihelper, types
from configparser import ConfigParser
from strings2 import *
from lxml.html import fromstring as fs
from requests import get
from json import loads
import logging as log

log.basicConfig(format = u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', level = log.DEBUG)

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
    log.debug('Making keyboard')
    markup = types.ReplyKeyboardMarkup()
    c = cities_list.split(',')
    buttons = [types.KeyboardButton(x) for x in c]
    markup.row(*buttons[:3])
    markup.row(*buttons[3:6])
    markup.row(*buttons[6:])
    return markup


@bot.message_handler(commands=['start', 'help'], func=lambda x: not x in cities)
def start(msg):
    log.info(str(msg.chat.id) + ' started messaging')
    if not cities.get(msg.chat.id):
        log.debug('No city specified for {}'.format(msg.chat.id))
        bot.send_message(msg.chat.id, hello_1)
        bot.send_message(msg.chat.id, hello_2)
        bot.send_message(msg.chat.id, ask_cities,
                         reply_markup=make_city_keyboard())
    else:
        log.debug('City for {} is {}'.format(msg.chat.id, cities[msg.chat.id]))
        bot.send_message(msg.chat.id, hello_3,
                         reply_markup=types.ReplyKeyboardRemove())
        stage[msg.chat.id] = 'search'


@bot.message_handler(func=lambda x: x.text in cities_list.split(','))
def write_city(msg):
    log.info('{} selected {} as a city'.format(msg.chat.id, msg.text))
    cities[msg.chat.id] = msg.text
    start(msg)


@bot.message_handler(func=lambda x: stage.get(x.chat.id) == 'search')
def search(msg):
    log.debug('{} is searching for {}'.format(msg.chat.id, msg.text))
    suggestions = get(cfg['eapteka']['base'].format(
        msg.text)).json().get('suggestions')
    if not suggestions:
        bot.send_message(msg.chat.id, no_suggestions)
        return
    s = select_number + '\n\n'
    for pair in enumerate(suggestions, 1):
        s += "{}) {}\n".format(*pair)
    bot.send_message(msg.chat.id, s)
    search_results[msg.chat.id] = suggestions
    stage[msg.chat.id] = 'show_info'


@bot.message_handler(func=lambda x: x.text.strip().isdigit() and stage.get(x.chat.id) == 'show_info' and 0 < int(x.text) <= len(search_results.get(x.chat.id, 0)))
def show_info(msg):
    log.debug('{} selected number {}'.format(msg.chat.id, msg.text))
    page = fs(get(cfg['eapteka']['info'].format(
        search_results[msg.chat.id][int(msg.text) - 1], cities[msg.chat.id] if cities[msg.chat.id] in cities_list.split(',') else all_cities)).text)
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
    log.debug('{} sent something wrong: {}'.format(msg.chat.id, msg.text))
    bot.send_message(msg.chat.id, not_resolved)


log.info('Bot started')
bot.polling()
