__author__ = 'changye'

from urllib import request
import re
import logging


def convert_str_to_number(string):
    if type(string) is not str:
        return string
    m = re.match('^[\d]+[\.][\d]*$', string)
    if m:
        return float(string)
    m = re.match('^[\d]+$', string)
    if m:
        return int(string)
    else:
        return string


def str_to_number(strings):
    if type(strings) is list:
        return [convert_str_to_number(x) for x in strings]
    else:
        return convert_str_to_number(strings)


def format_quote(str):
    string = str.strip()

    if string == '':
        return None

    m = re.match(r'var hq_str_(\S+)="(.*)"', string)
    if m and len(m.groups()) > 1:

        stockInfo = dict()
        stockInfo['id'] = m.group(1)
        logging.info(stockInfo['id'])
        stockInfoArray = re.split(r'[\,]+', m.group(2))
        if len(stockInfoArray) < 1:
            return None
        logging.info(stockInfoArray)
        keys = ['name', 'open_today', 'close_yesterday', 'quote',
                'highest', 'lowest', 'buy', 'sell', 'deal', 'amount']
        for i, value in enumerate(keys):
            stockInfo[value] = str_to_number(stockInfoArray[i])

        stockInfo['buy_quote'] = str_to_number(stockInfoArray[11:21:2])
        stockInfo['buy_quantity'] = str_to_number(stockInfoArray[10:20:2])
        stockInfo['sell_quote'] = str_to_number(stockInfoArray[21:31:2])
        stockInfo['sell_quantity'] = str_to_number(stockInfoArray[20:30:2])
        stockInfo['date'] = str_to_number(stockInfoArray[30])
        stockInfo['time'] = str_to_number(stockInfoArray[31])

        logging.info(stockInfo)

        return stockInfo
    else:
        return None


def get_sina_quote(ids):

    if ids == '' or ids is None or len(ids) == 0:
        return None

    quoteId = ','.join(ids)
    # url = r'http://hq.sinajs.cn/list=' + quoteId
    url = r'http://112.90.6.246/list=' + quoteId
    logging.info("connecting:\t" + url)
    with request.urlopen(url) as f:
        data = f.read()

    quoteMsg = data.decode('gb2312').replace('\n', '')
    quotes = [x for x in quoteMsg.split(';') if x != '']
    logging.info(quotes)
    result = dict()
    for x in quotes:
        formated_quote = format_quote(x)
        result[formated_quote['id']] = formated_quote
    # return [format_quote(x) for x in quotes]
    return result

def get_average_price_of_certain_amount_buy(hq, amount):
    total = 0
    index = 0
    total_price = 0
    totol_can_buy = hq['sell_quantity'][0] + hq['sell_quantity'][1] + hq['sell_quantity'][2] + hq['sell_quantity'][3]
    while total <= amount and index < 4:
        volume = hq['sell_quantity'][index]
        price = hq['sell_quote'][index]
        max_canbuy = total + volume
        if max_canbuy > amount:
            total_price = total_price + (amount - total) * price
            total = amount
        else:
            total_price = total_price + volume * price
            total = total + volume
        index += 1
    if total == 0:
        return (0 , 0, 0, 0)
    else:
        return (total_price / total, total, totol_can_buy, hq['sell_quote'][3])


def get_average_price_of_certain_amount_sell(hq, amount):
    total = 0
    index = 0
    total_price = 0
    totol_can_sell = hq['buy_quantity'][0] + hq['buy_quantity'][1] + hq['buy_quantity'][2] + hq['buy_quantity'][3]
    while total <= amount and index < 4:
        volume = hq['buy_quantity'][index]
        price = hq['buy_quote'][index]
        max_cansell = total + volume
        if max_cansell > amount:
            total_price = total_price + (amount - total) * price
            total = amount
        else:
            total_price = total_price + volume * price
            total = total + volume
        index += 1
    if total == 0:
        return (0 , 0, 0, 0)
    else:
        return (total_price / total, total, totol_can_sell, hq['buy_quote'][3])


if __name__ == '__main__':
    print(get_quote(['sz150209', 'sz150221']))
    # print(str_to_number(['hello', '1.23', '3432']))