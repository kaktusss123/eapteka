import strings
from Bot import *
from config import TOKEN, MY_ID
from json import loads
from requests import get
from lxml import html

OFFSET = 0
USERS = {}
CART = {}
TEMP_SEARCH_RESULTS = {}


def main_menu(bot, id, message):
    global USERS
    message = message.lower()
    if message == '/start':
        bot.send_message(id, strings.hello_1)
        bot.send_message(id, strings.hello_2, keyboard=strings.main_keyboard)
    elif message not in strings.main_commands:
        bot.send_message(id, 'Команда не найдена, выбери из списка😉', keyboard=strings.main_keyboard)
    else:
        if message == 'найти товар':
            USERS[id] = search
            bot.send_message(id, 'Напиши мне название товара, и я попробую его найти')


def search(bot, id, message):
    global USERS, TEMP_SEARCH_RESULTS
    message = message.lower()
    resp = loads(get('http://e-apteka.md/ajax/search_products.php?query=' + message).text)['data']
    if not resp:
        bot.send_message(id, 'По запросу ничего не найдено, попробуй еще раз✏')
    else:
        USERS[id] = choice
        s = strings.search_results_header.format(message)
        for i, n in enumerate((i['name'] for i in resp), 1):
            s += f'{i}) {n}\n'
        s += strings.search_results_bottom
        TEMP_SEARCH_RESULTS[id] = resp
        bot.send_message(id, s)


def parse_info(name):
    product = html.fromstring(get('http://e-apteka.md/products?keyword=' + name).text).xpath('//div[@class="product"]')
    image = product.xpath('./div[@class="image"]/a/@href')
    try:
        producer = product.xpath('./div[@style="width:245px;height:106px;float:left;"]/br')[1]
    except:
        producer = None
    active = product.xpath('./div[@class="description yobject-marked"]/text()')
    print(name, image, producer, active)


def choice(bot, id, message):
    global TEMP_SEARCH_RESULTS
    print(TEMP_SEARCH_RESULTS)
    if not message.strip().isdigit():
        bot.send_message(id, strings.not_a_number)
    elif not 0 <= int(message) < len(TEMP_SEARCH_RESULTS[id]):
        bot.send_message(id, strings.wrong_range)
    else:
        parse_info(TEMP_SEARCH_RESULTS[id][int(message)]['name'])
        # USERS[id] = item_info
        # Показать инфу


def start(bot):
    global OFFSET, USERS

    updates = bot.get_updates(OFFSET)

    if updates:
        OFFSET = updates[-1]['update_id'] + 1

    for update in updates:
        id = update['message']['from']['id']
        if id not in USERS:
            USERS[id] = main_menu
        else:
            try:
                text = update['message']['text']
                USERS[id](bot, id, text)
            except KeyError:
                bot.forward_message(MY_ID, update['message']['chat']['id'], update['message']['message_id'])


if __name__ == '__main__':
    try:
        bot = BotHandler(TOKEN)
        while 1:
            start(bot)
    except:
        print('exception')
        bot = BotHandler(TOKEN)
        while 1:
            start(bot)
