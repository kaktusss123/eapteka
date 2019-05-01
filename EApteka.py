from requests import Session, get
from json import loads
from pprint import pprint


def search(session, query):
    BASE = 'http://e-apteka.md/ajax/search_products.php?query='
    server_response = loads(session.get(BASE + query).text)
    response = 'Выбери товар из списка (0 - отмена):\n'
    for i, n in enumerate((i['name'] for i in server_response['data']), 1):
        response += f'{i}) {n}\n'
    return server_response


def dialogue():
    s = Session()
    temp_results = search(s, 'аспирин')
    response = 'Выбери товар из списка (0 - отмена):\n'
    for i, n in enumerate((i['name'] for i in temp_results), 1):
        response += f'{i}) {n}\n'
    return response


def parse_info(name):
    resp = get('http://e-apteka.md/products?keyword=' + name).text
    return resp


if __name__ == '__main__':
    print(parse_info('Аспирин Кардио таб 100мг №20'))
