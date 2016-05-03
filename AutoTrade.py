from datetime import datetime
from time import sleep
from Trade.Trader import Trader
from Trade.Quotation import *
import logging
logging.basicConfig(level=logging.INFO)

#
# Created by 'changye'  on '15-10-27'
#
__author__ = 'changye'


class AutoTrade(object):
    def __init__(self, trade_account, trade_password, notifier, ocr, step_interval=0.5, simulate=True):
        self.__notifier = notifier

        self.__trader = Trader(trade_account, trade_password, notifier=self.__notifier, ocr_service=ocr)

        self.__modules = list()
        self.__focus_list = list()
        self.__quotes = list()
        self.__simulate = simulate
        self.__step_interval = step_interval

        self.__current_time = datetime.now()
        self.__market_close_time = datetime.now().replace(hour=15, minute=10, second=00)

    def report(self, level='INFO', message='I am ok!'):

        logging.warning('[%s] %s' % (datetime.now().strftime('%m%d-%H:%M:%S'), message))

        if not self.__notifier:
            self.__notifier.send('%s[%s]' % (level, datetime.now().strftime('%m%d-%H:%M:%S')), message)

    # 交易系统退出的条件, 如果判读符合条件,则退出交易系统
    def ready_to_exit(self):
        """
        判断交易系统是否符合退出的条件, 暂定为市场关闭后自动退出
        :return: 当市场关闭后(15:00之后), 返回True, 否则返回False
        :rtype: bool
        """
        if self.__current_time > self.__market_close_time:
            logging.warning('现在不是交易时间, 自动退出交易, 如果需要改变退出条件,请修改 AutoTrade.py的ready_to_exit函数')
            return True
        return False

    # 退出系统
    def exit(self):
        """
        退出系统
        :return:
        :rtype:
        """
        self.__trader.sign_out_socket()
        self.__trader.exit()
        # self.report('INFO', 'AutoTrade system Now exit!')

    # 载入module
    def load_module(self, module):
        """
        module载入函数
        :param module: module的实例
        :type module: Modules.Module.Module
        :return:
        :rtype:
        """
        # 初始化module
        module_no = len(self.__modules)
        # 给module设置trader
        module.set_trader(self.__trader)
        # 准备module, 通常在该步骤读取config文件, 或者获取账户信息
        module.prepare(module_no)
        # 将module加入列表
        self.__modules.append(module)

    # 获取module的关注列表
    def __get_focus_list_from_module(self):
        """
        获取module的关注列表
        :return:
        :rtype:
        """
        focus_list = list()
        for m in self.__modules:
            focus_list += m.focus_list()
        self.__focus_list = focus_list

    # 获取focus_list的报价
    def __get_quote_of_focus_list(self):
        """
        获取关注列表的报价
        :return:
        :rtype:
        """
        self.__quotes = get_quote(self.__focus_list)

    # 将报价提供给modules, 触发module的判断机制
    def __feed_quotes_back_to_modules(self):
        """
        将报价提供给modules, 触发module的判断机制
        :return:
        :rtype:
        """
        for m in self.__modules:
            jobs = m.need_to_trade(self.__quotes, self.__current_time)
            if jobs is not None:
                self.__trader.add_jobs_to_pending_list(jobs)

    def prepare(self):

        self.__trader.initial_socket()

        signed_in = self.__trader.sign_in_socket()

        if not signed_in:
            auto.report('WARN', 'Can not login!')
            exit()

        # auto.report('WARN', 'Login successfully!')

    def start(self):

        self.__trader.start()

        self.__get_focus_list_from_module()

        while not self.ready_to_exit():

            self.__current_time = datetime.now()

            self.__get_quote_of_focus_list()

            self.__feed_quotes_back_to_modules()

            sleep(self.__step_interval)

        self.exit()


if __name__ == '__main__':

    import json
    # 配置校验码识别系统的用户名和密码(校验码识别由ruokuai.com提供, 请注册该网站的用户(非开发者))
    config_ocr = dict()
    with open('Configs/Tools.config.ocr', 'r') as f:
        config_ocr = json.loads(f.read().replace(r'\n', ''))

    from Tools.Ocr import Ocr
    my_ocr = Ocr(config_ocr['account'], config_ocr['password'])


    config = dict()
    with open('Configs/Socket.config.gf', 'r') as f:
        config = json.loads(f.read().replace(r'\n', ''))
    auto = AutoTrade(config['account'], config['password'], notifier=None, ocr=my_ocr)

    auto.prepare()

    # 导入第一个模块 heart_beat, 该模块的作用是防止trader因为长时间无操作而过期
    from Modules.HeartBeat import HeartBeat
    heart_beat = HeartBeat(heart_beat_interval_in_minutes=0.5)
    auto.load_module(heart_beat)



    # 开始运行
    auto.start()




