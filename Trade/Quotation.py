#
# Created by 'changye'  on '16-1-6'
#
from Tools.SinaApi import *

__author__ = 'changye'


def get_quote(focus_list):
    return get_sina_quote(focus_list)


def get_average_price_of_certain_amount_buy(hq, amount):
    total = 0
    index = 0
    total_price = 0
    total_can_buy = hq['sell_quantity'][0] + hq['sell_quantity'][1] + hq['sell_quantity'][2] + hq['sell_quantity'][3]
    while total <= amount and index < 4:
        volume = hq['sell_quantity'][index]
        price = hq['sell_quote'][index]
        max_canbuy = total + volume
        if max_canbuy > amount:
            total_price += (amount - total) * price
            total = amount
        else:
            total_price = total_price + volume * price
            total = total + volume
        index += 1
    if total == 0:
        return 0, 0, 0, 0
    else:
        return total_price / total, total, total_can_buy, hq['sell_quote'][3]


def get_average_price_of_certain_amount_sell(hq, amount):
    total = 0
    index = 0
    total_price = 0
    total_can_sell = hq['buy_quantity'][0] + hq['buy_quantity'][1] + hq['buy_quantity'][2] + hq['buy_quantity'][3]
    while total <= amount and index < 4:
        volume = hq['buy_quantity'][index]
        price = hq['buy_quote'][index]
        max_cansell = total + volume
        if max_cansell > amount:
            total_price += (amount - total) * price
            total = amount
        else:
            total_price = total_price + volume * price
            total = total + volume
        index += 1
    if total == 0:
        return 0, 0, 0, 0
    else:
        return total_price / total, total, total_can_sell, hq['buy_quote'][3]
