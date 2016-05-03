#
# Created by 'changye'  on '15-10-29'
#

__author__ = 'changye'

import abc
from Trade.Job import Job
from Trade.Quotation import *
import logging
from datetime import datetime, date


class Module(object, metaclass=abc.ABCMeta):

    def __init__(self):
        self.__module_no = -1
        self.__job_serial_no = 0
        self.__trader = None
        self.quotes = list()

    def prepare(self, module_no):
        self.__module_no = module_no
        logging.warning('preparing %s(%d)' % (self.__class__, self.__module_no))

    def set_trader(self, trader):
        self.__trader = trader

    def create_new_job(self, time_stamp, simulate=False):
        job = Job(self.__module_no, self.__job_serial_no, time_stamp)
        if simulate is True:
            job.set_simulate(True)
        self.__job_serial_no += 1
        return job

    @staticmethod
    def check_current_time_to(self, hour=00, minute=00, second=00):
        """
        检查当前时间和目标时间的关系
        :param hour: hour 范围0-23
        :type hour: int
        :param minute: 范围0-59
        :type minute: int
        :param second: 范围0-59
        :type second: int
        :return: 当前时间大于目标时间时返回1, 当前时间等于目标时间时返回0, 当前时间小于目标时间时返回-1
        :rtype: int
        """
        now = datetime.now()
        target = datetime.now().replace(hour=hour, minute=minute, second=second)
        if now > target:
            return 1
        if now == target:
            return 0
        if now < target:
            return -1

    @staticmethod
    def check_current_date_to(year=datetime.now().year, month=1, dates=1):
        """
        检查当前日期和目标日期的关系
        :param year: 年
        :type year: int
        :param month: month
        :type month: int
        :param date: date
        :type date: int
        :return: 当前日期大于目标日期时返回1, 当前日期等于目标日期时返回0, 当前日期小于目标日期时返回-1
        :rtype: int
        """
        now = datetime.now().date()
        target = date(year, month, dates)
        if now > target:
            return 1
        if now == target:
            return 0
        if now < target:
            return -1

    def ask_at_price(self, code, market, amount, price, time_stamp):
        job = self.create_new_job(time_stamp)\
            .set(Job.SELL, code, market, amount, price, msg='挂单: sell %d of %s @ %.3f' % (amount, code, price))
        return job

    def bid_at_price(self, code, market, amount, price, time_stamp):
        job = self.create_new_job(time_stamp)\
            .set(Job.BUY, code, market, amount, price, msg='挂单: buy %d of %s @ %.3f' % (amount, code, price))
        return job

    def buy_when_price_exceed(self, code, market, amount, price, time_stamp):
        """
        在价格低于某个值时购买
        :param code: 代码
        :type code: str
        :param market: 市场, sh或sz
        :type market: str
        :param amount: 数量
        :type amount: int
        :param price: 价格
        :type price: float
        :param time_stamp: 时间戳
        :type time_stamp: datetime
        :return: None为失败, 成功返回job
        :rtype: Job
        """

        query_code = market + code

        if query_code not in self.quotes:
            return None
        quote = self.quotes[query_code]
        average_price, amount_buy, amount_all_ask, highest_price \
            = get_average_price_of_certain_amount_buy(quote, amount)

        if average_price <= price and amount_buy >= amount:
            job = self.create_new_job(time_stamp)\
                .set(Job.BUY, code, market, amount, price,
                     msg='市场价格%.3f小于等于目标价格%.3f, 买入%s %d股' % (average_price, price, code, amount))
            return job
        else:
            return None

    def sell_when_price_exceed(self, code, market, amount, price, time_stamp):
        """
        在价格高于某个值时卖出
        :param code: 代码
        :type code: str
        :param market: 市场, sh或sz
        :type market: str
        :param amount: 数量
        :type amount: int
        :param price: 价格
        :type price: float
        :param time_stamp: 时间戳
        :type time_stamp: datetime
        :return: None为失败, 成功返回job
        :rtype: Job
        """

        query_code = market + code

        if query_code not in self.quotes:
            return None
        quote = self.quotes[query_code]
        average_price, amount_sell, amount_all_bid, lowest_price \
            = get_average_price_of_certain_amount_sell(quote, amount)

        if average_price >= price and amount_sell >= amount:
            job = self.create_new_job(time_stamp)\
                .set(Job.SELL, code, market, amount, price,
                     msg='市场价格%.3f大于等于目标价格%.3f, 卖出%s %d股' % (average_price, price, code, amount))
            return job
        else:
            return None

    @property
    def module_no(self):
        return self.__module_no

    @abc.abstractmethod
    def focus_list(self):
        raise NotImplementedError('focus_list must be defined.')

    def need_to_trade(self, quotes, time_stamp):
        self.quotes = quotes

    def get_stock_position(self, force_refresh=False):
        return self.__trader.get_stock_position()

    def get_balance(self, force_refresh=False):
        return self.__trader.get_balance()

    def check_job_status(self, job):
        return self.__trader.check_job_status(job)
