#!/usr/bin/python3
import strings
from Bot import *
from config import TOKEN, MY_ID
from json import loads
from requests import get
from lxml import html

OFFSET = 0
USERS = {}
CART = {}
SELECTED_ITEM = {}
TEMP_SEARCH_RESULTS = {}
SEARCH_QUERY = {}


def main_menu(bot, id, message):
    global USERS
    message = message.lower()
    if message == '/start':
        # bot.send_message(id, strings.hello_1)
        bot.send_message(id, strings.hello_2, keyboard=strings.main_keyboard)
    if message not in strings.main_commands:
        bot.send_message(id, 'Команда не найдена, выбери из списка😉', keyboard=strings.main_keyboard)
    elif message == 'найти товар':
        USERS[id] = search
        bot.send_message(id, 'Напиши мне название товара, и я попробую его найти')


def search(bot, id, message):
    global USERS, TEMP_SEARCH_RESULTS, SEARCH_QUERY
    message = message.lower()
    resp = loads(get('http://e-apteka.md/ajax/search_products.php?query=' + message).text)['data']
    if not resp:
        bot.send_message(id, 'По запросу ничего не найдено, попробуй еще раз✏')
    else:
        USERS[id] = choice
        s = strings.search_results_header.format(message)
        SEARCH_QUERY[id] = message
        for i, n in enumerate((i['name'] for i in resp), 1):
            s += '{}) {}\n'.format(i, n)
        s += strings.search_results_bottom
        TEMP_SEARCH_RESULTS[id] = resp
        bot.send_message(id, s)


def parse_info(bot, id, name):
    global USERS, SELECTED_ITEM
    # TODO: должно заработать с единым справочником
    # пример: Аспирин 3
    product = html.fromstring(get('http://e-apteka.md/products?keyword=' + name).text).xpath('//div[@class="product"]')[
        0]
    image = product.xpath('./div[@class="image"]/a/@href')
    try:
        price = strings.price.format(
            product.xpath('.//table[@style="font: 15px arial;"]//span[@class="price"]/text()')[0])
    except:
        price = strings.out_of_stock
    # отправить фото
    s = '{}\n\n{}'.format(name, price)
    if price != strings.out_of_stock:
        bot.send_photo(id, image, s, keyboard=strings.to_cart_keyboard)
    else:
        bot.send_photo(id, image, s, keyboard=strings.to_cart_out_keyboard)
    SELECTED_ITEM[id] = name
    USERS[id] = item_info


def item_info(bot, id, message):
    global USERS, CART, SEARCH_QUERY
    if message.lower() == 'добавить':
        if not CART[id]:
            CART[id] = []
        CART[id].append(SELECTED_ITEM[id])
        bot.send_message(id, strings.added, keyboard=strings.to_cart_next_keyboard)
        print(CART)
    else:
        USERS[id] = search
        USERS[id](bot, id, SEARCH_QUERY[id])


def choice(bot, id, message):
    global TEMP_SEARCH_RESULTS
    if not message.strip().isdigit():
        bot.send_message(id, strings.not_a_number)
    elif not 0 <= int(message) <= len(TEMP_SEARCH_RESULTS[id]):
        bot.send_message(id, strings.wrong_range)
    else:
        if not int(message):
            USERS[id] = main_menu
            USERS[id](bot, id, '/start')
        else:
            parse_info(bot, id, TEMP_SEARCH_RESULTS[id][int(message) - 1]['name'])
            USERS[id] = item_info
        # Показать инфу


def start(bot):
    global OFFSET, USERS

    updates = bot.get_updates(OFFSET)

    if updates:
        OFFSET = updates[-1]['update_id'] + 1

    for update in updates:
        id = update['message']['from']['id']
        if id not in USERS:
            bot.send_message(id, strings.hello_1)
            USERS[id] = main_menu
        try:
            text = update['message']['text']
            USERS[id](bot, id, text)
        except KeyError as e:
            bot.forward_message(MY_ID, update['message']['chat']['id'], update['message']['message_id'])
            bot.error(update)


if __name__ == '__main__':
    # try:
    bot = BotHandler(TOKEN)
    while 1:
        start(bot)
# except:
#     print('exception')
#     bot = BotHandler(TOKEN)
#     while 1:
#         start(bot)
