#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from requests import get


def parse_info(name):
    resp = get('http://e-apteka.md/products?keyword=' + name).text
    return resp


if __name__ == '__main__':
    print(parse_info('Аспирин Кардио таб 100мг №20'))
