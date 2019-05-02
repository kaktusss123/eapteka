#!/usr/bin/python3
from requests import get
from lxml import html

def parse_info(name):
    resp = get('http://e-apteka.md/products?keyword=' + name).text
    page = html.fromstring(resp)
    with open('test.html', 'w') as f:
        f.write(resp)
    return page.xpath('//div[@class="description"]/text()')[6]


if __name__ == '__main__':
    print(parse_info('Аспирин Кардио таб 100мг №20'))
