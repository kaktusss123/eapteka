from requests import get


def parse_info(name):
    resp = get('http://e-apteka.md/products?keyword=' + name).text
    return resp


if __name__ == '__main__':
    print(parse_info('������� ������ ��� 100�� �20'))
