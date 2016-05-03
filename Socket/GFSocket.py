from Socket.Socket import Socket
import uuid
import re
import requests
from random import random as rand
import json
from PIL import Image
from time import sleep, time, strftime
import logging
# logging.basicConfig(level=logging.INFO)
#
# Created by 'changye'  on '15-9-03'
# Email: changye17@163.com
#
# 广发交易接口
# 测试环境: WIN7  python3.4
# 注意事项:
#   调用try_auto_login() 自动OCR 需要安装tesseract-ocr
#   调用show_verify_code() 自动显示验证码,需要安装imagemagick
#
# 使用方法:
# 初始化
# gf = GFSocket('encrypted_account','encrypted_password')
#
# 自动登录:
# while(not gf.try_auto_login()):
#     time.sleep(3)
#
# 手动登录:
# gf.prepare_login()                      第一步,读取验证码
# gf.show_verify_code()                   第二步,显示验证码(也可省略,直接看目录下vericode.jsp文件)
# vericode = input("input verify code: ")
# gf.enter_verify_code(vericode)          第三步,输入验证码
# gf.login()                              第四步,登陆 成功返回True,失败返回False
# gf.prepare_trade()                      第五步,获取交易参数, 完成此步后即可进行交易.
#
#
# gf可读取参数
# gf.balance              账目信息,字典
# {
# 'mortgage_balance': '0',
# 'square_flag': ' ',
# 'money_type_dict': '人民币',
# 'foregift_balance': '0',
# 'pre_interest': '0',
# 'entrust_buy_balance': '0',
# 'bank_name': '',
# 'fund_account': 'xxxxx',
# 'opfund_market_value': '0',
# 'enable_balance': '0',                    可用
# 'market_value': '0',
# 'pre_interest_tax': '0',
# 'rate_kind': ' ',
# 'asset_prop': '0',
# 'integral_balance': '0',
# 'pre_fine': '0',
# 'money_type': '0',
# 'begin_balance': '0',
# 'interest': '0',
# 'main_flag': '1',
# 'fetch_cash': '0',                        可取
# 'fetch_balance_old': '0',
# 'net_asset': 19090.0,                     净资产
# 'frozen_balance': '0',
# 'asset_balance': 19090.0,                 资产
# 'correct_balance': '0',
# 'current_balance': 19090.0,               当前账目
# 'unfrozen_balance': '0',
# 'fetch_balance': '0',
# 'fund_balance': 19090.0,
# 'bank_no': '',
# 'fine_integral': '0'
# }

# gf.stock_position       仓位信息,列表,列表元素为字典
# {
# 'delist_flag': '0',
# 'entrust_sell_amount': '0',
# 'real_buy_amount': 100.0,
# 'av_income_balance': '0',
# 'income_balance': '-29.70',
# 'exchange_type': '1',
# 'stock_type': 'j',
# 'keep_cost_price': 100.305,
# 'exchange_type_dict': '上海',
# 'delist_date': '0',
# 'market_value': 10000.8,
# 'cost_price': 100.305,
# 'enable_amount': 100.0,          可用
# 'last_price': 100.008,
# 'cost_balance': 10030.5,
# 'par_value': 1.0,
# 'hold_amount': '0',
# 'frozen_amount': '0',
# 'av_buy_price': '0',
# 'stock_account': 'XXXXXXXX',
# 'position_str': 'XXX',
# 'income_balance_nofare': '-29.70',
# 'fund_account': '12321435',
# 'stock_name': '华宝添益',
# 'uncome_buy_amount': '0',
# 'asset_price': 100.008,
# 'client_id': '020290017429',
# 'stock_code': '511990',           代码
# 'real_sell_amount': '0',
# 'uncome_sell_amount': '0',
# 'hand_flag': '0',
# 'current_amount': 100.0           持仓
# }
# gf.cancel_list          可撤单清单,列表,列表元素为字典

# gf.entrust_list         委托清单,列表,列表元素为字典
# {
# 'business_amount': '0',
# 'entrust_amount': 1.0,
# 'report_milltime': '83902147',
# 'entrust_price': 1.0,
# 'init_date': '20150910',
# 'report_no': '169',
# 'curr_milltime': '81129637',
# 'entrust_status': '8',
# 'stock_account': 'XXXXXXXX',
# 'business_balance': '0',
# 'entrust_date': '20150910',
# 'entrust_way': '4',
# 'stock_code': '799999',
# 'entrust_no': '169',
# 'entrust_type': '0',
# 'stock_name': '登记指定',
# 'business_price': '0',
# 'entrust_bs_dict': '买入',
# 'cancel_info': ' ',
# 'entrust_type_dict': '委托',
# 'entrust_prop': '6',
# 'entrust_bs': '1',
# 'fund_account': 'XXXXXXX',
# 'exchange_type': '1',
# 'entrust_time': '81129',
# 'position_str': 'XXXXXXXX',
# 'report_time': '83902',
# 'withdraw_amount': '0',
# 'entrust_status_dict': '已成',
# 'batch_no': '169'
# }

# gf.trade_list           成交清单,列表,列表元素为字典
# {
# 'business_time': '100149',
# 'business_times': '1',
# 'business_amount': 100.0,
# 'stock_name': '华宝添益',
# 'position_str': '20150910041001495380020200004584',
# 'business_price': 100.005,
# 'entrust_prop': '0',
# 'entrust_bs': '1',
# 'report_no': '5250',
# 'exchange_type': '1',
# 'entrust_bs_dict': '买入',
# 'serial_no': '4584',
# 'business_no': '3779535',
# 'date': '20150910',
# 'business_balance': 10000.5,
# 'stock_code': '511990',
# 'stock_account': 'XXXXXX',
# 'fund_account': 'XXXXXX',
# 'real_type': '0',
# 'real_status': '0',
# 'entrust_no': '5250'
# }

# gf可操作函数
# 买入,成功返回委托号,如果失败返回None
# gf.buy(code='600036', amount=100, price=6.66, market='sh')
#
# 卖出,成功返回委托号,如果失败返回None
# gf.sell(code='600036', amount=100, price=6.66, market='sh'))
#
# 撤单,成功返回委托号,如果失败返回None
# gf.cancel(entrust_no='12345')
# gf.cancel_all()

# 下面的函数为内部函数,请不要直接运行
# 连接站点并获取信息,成功返回True,失败返回False
# gf._get_balance()       获取账目
# gf._get_position()      获取仓位
# gf._get_cancel_list()   获取可撤单列表
# gf._get_today_entrust() 获取今日委托列表
# gf._get_today_trade()   获取今日成交列表


__author__ = 'changye'


class GFSocket(Socket):

    def __init__(self, encrypted_account, encrypted_password,
                 hd_model="WD-WX31C32M1910", retry_time=3, retry_interval=0.5):

        # 加密后的用户账号
        self.__encrypted_account = encrypted_account

        # 用户加密后的交易密码
        self.__encrypted_password = encrypted_password

        # 用户硬盘型号
        self.__harddisk_model = hd_model

        # # 用户类型
        # self.__user_type = "jy"

        # 获取mac地址
        self.__mac_addr = ':'.join(re.findall('..', '%012x' % uuid.getnode()))
        logging.info(self.__mac_addr)

        # 获取ip地址
        self.__ip_addr = '192.168.1.123'
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("baidu.com", 80))
            self.__ip_addr = s.getsockname()[0]
        finally:
            if s:
                s.close()
        logging.info(self.__ip_addr)

        # 验证码
        self.__verify_code = ""

        # 欢迎页面,可在该页面获得验证码
        self.__welcome_page = "https://trade.gf.com.cn/"

        # 验证码地址
        self.__verify_code_page = "https://trade.gf.com.cn/yzm.jpgx?code="
        self.__verify_code_length = 5

        # 登录页面
        self.__login_page = "https://trade.gf.com.cn/login"

        # 交易接口
        self.__trade_page = "https://trade.gf.com.cn/entry"

        # 初始化浏览器
        self.__browser = requests.session()
        # 设置user-agent
        self.__browser.headers['User-Agent'] = 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)'

        # 交易传输dse_sessionId
        self.__dse_sessionId = None

        # 股东账号
        # 上海
        self.__market_account_sh = None
        # 深圳
        self.__market_account_sz = None

        # # 交易参数
        # self.__trade_version = 1
        # self.__op_entrust_way = 7

        # 账目信息
        # 账目信息为一个字典
        self.__balance = None

        # 持仓信息
        # 持仓为一个数组,即list()
        # 数组中的元素为字典
        self.__stock_position = None

        # 可撤单交易列表
        # 可撤单交易列表为一个数组,即list()
        # 数组中的元素为字典,其内容示例为:
        # {
        #     'entrust_amount': 1000.0,     委托数量
        #     'exchange_type': '1',
        #     'entrust_prop': '0',
        #     'entrust_status': '2',        2为已报;
        #     'business_amount': '0',
        #     'business_price': '0',
        #     'entrust_no': '24555',        委托号
        #     'entrust_time': '110952',
        #     'entrust_price': 102.5,       委托价格
        #     'stock_name': '银华日利',
        #     'exchange_name': '上海Ａ',
        #     'bs_name': '买入',
        #     'stock_account': 'A11111111', 股东账户
        #     'stock_code': '511880',       股票代码
        #     'entrust_bs': '1',            1为买入;2为卖出
        #     'status_name': '已报',
        #     'prop_name': '买卖'
        # }
        self.__cancel_list = None

        # 当日委托列表
        # 当日委托列表为一个数组,即list()
        # 数组中的元素为字典,其内容示例为:
        # {
        #     'entrust_price': 102.533,     委托价格
        #     'stock_account': 'A1111111',  股东账户
        #     'entrust_time': '110849',     委托时间
        #     'entrust_amount': 100.0,      委托数量
        #     'stock_name': '银华日利',
        #     'status_name': '已成',
        #     'exchange_type': '1',
        #     'prop_name': '买卖',
        #     'bs_name': '买入',
        #     'entrust_status': '8',        8为已成,9为废单,6为已撤,2为已报
        #     'entrust_no': '24410',        委托号
        #     'business_price': 102.533,
        #     'business_amount': 100.0,
        #     'entrust_prop': '0',
        #     'stock_code': '511880',       股票代码
        #     'entrust_bs': '1',            1为买入,2为卖出
        #     'exchange_name': '上海Ａ'
        # }
        self.__entrust_list = None

        # 当日成交列表
        # 当日成交列表为一个数组,即list()
        # 数组中的元素为字典,其内容示例为:
        # {
        #     'business_amount': 200.0,     成交数量
        #     'stock_code': '511990',       股票代码
        #     'date': '20150828',           成交日期
        #     'bs_name': '卖出',
        #     'remark': '成交',
        #     'business_balance': 20001.6,  成交金额
        #     'stock_name': '华宝添益',
        #     'exchange_type': '上海Ａ',
        #     'stock_account': 'A11111111', 股东账户
        #     'entrust_no': '26717',        委托号
        #     'business_price': 100.008,    成交均价
        #     'serial_no': '35486'          流水号
        # }
        self.__trade_list = None

        # 连接失败后,再次尝试的时间间隔
        self.__retry_interval = retry_interval
        # 连接失败后的尝试次数
        self.__retry_time = retry_time

    # @property
    def market_account_sh(self):
        return self.__market_account_sh

    # @property
    def market_account_sz(self):
        return self.__market_account_sz

    def verify_code_length(self):
        return self.__verify_code_length

    # @property
    def balance(self):
        counter = 0
        while (counter < self.__retry_time) and (not self._get_balance()):
            sleep(self.__retry_interval)
            counter += 1
        return self.__balance

    # @property
    def stock_position(self):
        counter = 0
        while (counter < self.__retry_time) and (not self._get_position()):
            sleep(self.__retry_interval)
            counter += 1
        return self.__stock_position

    # @property
    def cancel_list(self):
        counter = 0
        while (counter < self.__retry_time) and (not self._get_cancel_list()):
            sleep(self.__retry_interval)
            counter += 1
        return self.__cancel_list

    # @property
    def entrust_list(self):
        counter = 0
        while (counter < self.__retry_time) and (not self._get_today_entrust()):
            sleep(self.__retry_interval)
            counter += 1
        return self.__entrust_list

    # @property
    def trade_list(self):
        counter = 0
        while (counter < self.__retry_time) and (not self._get_today_trade()):
            sleep(self.__retry_interval)
            counter += 1
        return self.__trade_list

    # 获取验证码
    def get_verify_code(self):
        vericode_url = self.__verify_code_page + str(rand())
        # logging.info(vericode_url);
        resp = self.__browser.get(vericode_url)
        with open('./vericode.jpeg', 'wb') as file:
            file.write(resp.content)
        # logging.warning("verify code is stored in vericode.jsp. "
        #                 "use enter_verify_code() to input the code and then login()!")
        return './vericode.jpeg'

    # 显示验证码,需要安装imagemagick
    def show_verify_code(self):
        image = Image.open("./vericode.jpeg")
        image.show()

    # 识别验证码
    def recognize_verify_code(self):
        import tempfile
        import subprocess
        import os

        path = "./vericode.jpeg"

        temp = tempfile.NamedTemporaryFile(delete=False)
        process = subprocess.Popen(['tesseract', path, temp.name], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        process.communicate()

        with open(temp.name + '.txt', 'r') as handle:
            contents = handle.read()

        os.remove(temp.name + '.txt')
        os.remove(temp.name)

        return contents.replace(" ", "").replace("\n", "").replace("><", "x")

    # 输入验证码
    def enter_verify_code(self, text):
        self.__verify_code = text
        logging.warning("verify code is entered: " + text)

    # 登录准备,获取验证码
    def prepare_login(self):
        # 建立初始连接
        self.__browser.get(self.__welcome_page, verify=False)
        # 获取验证码
        return self.get_verify_code()

    # 输入加密后的账号和密码
    def enter_encrypted_account_and_password(self, encrypted_account, encrypted_password):
        self.__encrypted_account = encrypted_account
        self.__encrypted_password = encrypted_password

    # 获取当前毫秒数
    @staticmethod
    def __get_msec():
        return int(time() * 1000)

    # 将字典数据打包成字符串
    @staticmethod
    def __join_keys(keys):
        return '&'.join([k + "=" + str(keys[k]) for k in keys])

    # 将dict中的value转换为float,如果可能的话.
    # 因为部分股票代码,如000002是以0开头的,所以转化为int会造成股票代码的错误
    # 因此,即使可以转换为整数,也保持其字符串属性不变
    @staticmethod
    def __convert_value_in_dict_to_float(input_dict):
        result = dict()
        for (k, v) in input_dict.items():
            if re.match(r'^\d+\.\d+$', v):
                value = float(v)
            elif re.match(r'^\d+$', v):
                if k.find('account') < 0 and k.find('code') < 0:
                    value = int(v)
                else:
                    value = v
            else:
                value = v
            result[k] = value
        return result

    # 自动登录,并进入交易页面, 系统需要安装tesseract-ocr
    def try_auto_login(self):
        # 连接欢迎页面,获取验证码
        self.prepare_login()
        # 识别验证码
        verify_code = self.recognize_verify_code()
        # 输入验证码
        self.enter_verify_code(verify_code)
        # 登录
        return self.login()

    # 连接交易服务器,将query 和payload发送至交易服务区，并返回结果
    def __connect_trade_server(self, query, payload, no_judgement=False):
        # 每次发送携带的sessionId不能为None
        if self.__dse_sessionId is None:
            return None
        else:
            stamp = '&dse_sessionId=' + self.__dse_sessionId
        # 将query转化为字符串
        query_string = ''
        if query:
            query_string = '?' + self.__join_keys(query) + stamp

        if payload:
            payload['dse_sessionId'] = self.__dse_sessionId

        # 连接交易服务器
        url = self.__trade_page + query_string
        # logging.info(query_string)
        # for k, v in payload.items():
        #     logging.info('%s\t:\t%s' % (k, v))
        resp = self.__browser.post(url, data=payload)
        # 获取返回数据, 给key加上双引号
        content = resp.text.replace('\n', '').replace('\'', '\"')
        try:
            return_in_json = json.loads(content, parse_int=int)
            logging.info('return raw is: ' + content)
        except:
            content = re.sub(r'([^{":,]+):', '\"\\1\":', content)
            logging.info('return raw is: ' + content)
            return_in_json = json.loads(content)

        # 如果不需要判断是否返回正常,则直接返回数据.
        if no_judgement:
            return return_in_json
        # 判断返回数据是否成功
        if 'success' in return_in_json and return_in_json['success'] is True:
            return return_in_json
        else:
            return None


    # 登录
    def login(self):
        payload = {
            'username': self.__encrypted_account,
            'password': self.__encrypted_password,
            'tmp_yzm': self.__verify_code,
            'authtype': 2,
            'mac': self.__mac_addr,
            'disknum': self.__harddisk_model,
            'loginType': 2,
            'origin': 'web'
        }
        resp = self.__browser.post(self.__login_page, data=payload)
        content = resp.text.replace("\r\n", "")
        # 获取交易需要的sessionId
        self.__dse_sessionId = self.__browser.cookies.get('dse_sessionId')
        logging.info('dse_sessionId is: ' + str(self.__dse_sessionId))
        # with open('log', 'w') as f:
        #     f.write(content)
        login_return = json.loads(content)
        logging.info(str(login_return))
        if 'success' in login_return and login_return['success'] is True \
                and self.__dse_sessionId is not None:
            return True
        else:
            return False

    # 退出登录
    def logout(self):
        query = {}
        payload = {
            'classname': 'com.gf.etrade.control.AuthenticateControl',
            'method': 'logout'
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            return True
        else:
            return False

    # 获取股东账号
    def prepare_trade(self):
        query = {}
        payload = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'getStockHolders'
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            # 获取股票账户
            for market_account in result['data']:
                if 'exchange_type' in market_account:
                    if market_account['exchange_type'] == '1':
                        self.__market_account_sh = market_account['stock_account']
                    if market_account['exchange_type'] == '2':
                        self.__market_account_sz = market_account['stock_account']
            return True
        else:
            return False

    # 获取实时行情
    def get_realtime_quote(self, code):
        query = {}
        payload = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'getStockHQ',
            'stock_code': code
        }
        result = self.__connect_trade_server(query, payload, no_judgement=True)
        if 'hq' in result and 'success' in result['hq'] and result['hq']['success']:
            return result['hq']
        else:
            return None

    # 连接, 获取账户信息
    def _get_balance(self):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'queryFund',
            '_dc': self.__get_msec()
        }
        payload = {
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            for balance in result['data']:
                if 'money_type' in balance and balance['money_type'] == '0':
                    self.__balance = self.__convert_value_in_dict_to_float(balance)
            logging.info('balance is : ' + str(self.__balance))
            return True
        else:
            return False

    # 查询某个股票的可用余额
    def _get_enable_amount(self, stock_code, exchange_type):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'queryKYYE'
        }
        payload = {
            'stock_code': stock_code,
            'exchange_type': exchange_type
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            return result['data'][0]['enable_amount']
        else:
            return None

    def get_enable_amount(self, stock_code, market='sh'):
        if market == 'sh':
            return self._get_enable_amount(stock_code, 1)
        if market == 'sz':
            return self._get_enable_amount(stock_code, 2)
        return None

    # 连接服务器, 执行买入操作, 成功返回成交单号, 失败返回None
    def _buy(self, account, exchange_type, code, amount, price):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'entrust'
        }
        payload = {
            'exchange_type': exchange_type,    # 1为上海户, 2为深证户
            'stock_account': account,
            'stock_code': code,
            'entrust_amount': amount,
            'entrust_price': price,
            'entrust_prop': 0,
            'entrust_bs': 1
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            for order in result['data']:
                if 'entrust_no' in order:
                    return int(order['entrust_no'])
        return self.TRADE_FAIL

    # 连接服务器, 执行卖出操作, 成功返回成交单号, 失败返回None
    def _sell(self, account, exchange_type, code, amount, price):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'entrust'
        }
        payload = {
            'exchange_type': exchange_type,    # 1为上海户, 2为深证户
            'stock_account': account,
            'stock_code': code,
            'entrust_amount': amount,
            'entrust_price': price,
            'entrust_prop': 0,
            'entrust_bs': 2
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            for order in result['data']:
                if 'entrust_no' in order:
                    return int(order['entrust_no'])
        return self.TRADE_FAIL

    def _cancel_all(self, direction='all'):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'cancelall'
        }

        if direction == 'buy':
            query = {
                'classname': 'com.gf.etrade.control.StockUF2Control',
                'method': 'cancelbuy'
            }

        if direction == 'sell':
            query = {
                'classname': 'com.gf.etrade.control.StockUF2Control',
                'method': 'cancelsell'
            }
        payload = {}
        result = self.__connect_trade_server(query, payload)
        if result:
            return True
        else:
            return False

    # 连接服务器, 执行撤单操作, 成功返回True, 失败返回False
    def cancel(self, entrust_nos):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'cancels'
        }
        payload = {
            'entrust_nos': entrust_nos,
            'batch_flag': 0
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            return True
        else:
            return False

    # 连接服务器, 获取当日委托
    def _get_today_entrust(self):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'queryDRWT'
        }
        payload = {
            'query_direction': 0,
            'action_in': 0,
            'request_num': 100,
            'start': 0,
            'limit': 100
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            self.__entrust_list = list()
            for order in result['data']:
                if 'entrust_no' in order:
                    self.__entrust_list.append(self.__convert_value_in_dict_to_float(order))
            logging.info('entrust list is: ' + str(self.__entrust_list))
            return True
        else:
            return False

    # 连接服务器, 获取可撤单
    def _get_cancel_list(self):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'queryDRWT'
        }
        payload = {
            'query_direction': 0,
            'action_in': 1,
            'request_num': 100,
            'start': 0,
            'limit': 100
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            self.__cancel_list = list()
            for order in result['data']:
                if 'entrust_no' in order:
                    self.__cancel_list.append(self.__convert_value_in_dict_to_float(order))
            logging.info('entrust list is: ' + str(self.__cancel_list))
            return True
        else:
            return False

    # 连接服务器, 查询当日成交
    def _get_today_trade(self):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'queryDRCJ'
        }
        payload = {
            'query_direction': 0,
            'position_str': '',
            'query_mode': 0,
            'request_num': 100,
            'start': 0,
            'limit': 100
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            self.__trade_list = list()
            for order in result['data']:
                if 'entrust_no' in order:
                    self.__trade_list.append(self.__convert_value_in_dict_to_float(order))
            logging.info('trade list is: ' + str(self.__trade_list))
            return True
        else:
            return False

    # 连接服务器,获取仓位信息
    def _get_position(self):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'queryCC'
        }
        payload = {
            'request_num': 500,
            'start': 0,
            'limit': 0
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            self.__stock_position = list()
            for stock in result['data']:
                if 'exchange_type' in stock:
                    self.__stock_position.append(self.__convert_value_in_dict_to_float(stock))
            logging.info('stock position is: ' + str(self.__stock_position))
            return True
        else:
            return False

    # 上海lof交易: 申购
    def _sh_lof_purchase(self, exchange_type, stock_account, stock_code, price, amount):
        query = {
            'classname': 'com.gf.etrade.control.SHLOFFundControl',
            'method': 'assetSecuprtTrade'
        }
        payload = {
            'exchange_type': exchange_type,
            'stock_account': stock_account,
            'stock_code': stock_code,
            'entrust_price': price,
            'entrust_amount': amount,
            'entrust_prop': 'LFC',
            'entrust_bs': 1,
            'relation_name': '',
            'relation_tel': '',
            'prop_seat_no': '',
            'cbpconfer_id': '',
            'message_notes': ''
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            for order in result['data']:
                if 'entrust_no' in order:
                    return int(order['entrust_no'])
        else:
            return self.TRADE_FAIL

    def sh_lof_purchase(self, code, amount):
        return self._sh_lof_purchase(1, self.__market_account_sh, code, 1, amount)

    # 上海lof交易: 赎回
    def _sh_lof_redeem(self, exchange_type, stock_account, stock_code, price, amount):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'doDZJYEntrust'
        }
        payload = {
            'exchange_type': exchange_type,
            'stock_account': stock_account,
            'stock_code': stock_code,
            'entrust_price': price,
            'entrust_amount': amount,
            'entrust_prop': 'LFR',
            'entrust_bs': 2,
            'relation_name': '',
            'relation_tel': '',
            'prop_seat_no': '',
            'cbpconfer_id': '',
            'message_notes': ''
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            for order in result['data']:
                if 'entrust_no' in order:
                    return int(order['entrust_no'])
        else:
            return self.TRADE_FAIL

    def sh_lof_redeem(self, code, amount):
        return self._sh_lof_redeem(1, self.__market_account_sh, code, 1, amount)

    # 上海lof交易: 合并
    def _sh_lof_merge(self, exchange_type, stock_account, stock_code, price, amount):
        query = {
            'classname': 'com.gf.etrade.control.SHLOFFundControl',
            'method': 'assetSecuprtTrade'
        }
        payload = {
            'exchange_type': exchange_type,
            'stock_account': stock_account,
            'stock_code': stock_code,
            'entrust_price': price,
            'entrust_amount': amount,
            'entrust_prop': 'LFM',
            'entrust_bs': '',
            'relation_name': '',
            'relation_tel': '',
            'prop_seat_no': '',
            'cbpconfer_id': '',
            'message_notes': ''
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            for order in result['data']:
                if 'entrust_no' in order:
                    return int(order['entrust_no'])
        else:
            return self.TRADE_FAIL

    def sh_lof_merge(self, code, amount):
        return self._sh_lof_merge(1, self.__market_account_sh, code, 1, amount)

    # 上海lof交易: 分拆
    def _sh_lof_split(self, exchange_type, stock_account, stock_code, price, amount):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'doDZJYEntrust'
        }
        payload = {
            'exchange_type': exchange_type,
            'stock_account': stock_account,
            'stock_code': stock_code,
            'entrust_price': price,
            'entrust_amount': amount,
            'entrust_prop': 'LFP',
            'entrust_bs': '',
            'relation_name': '',
            'relation_tel': '',
            'prop_seat_no': '',
            'cbpconfer_id': '',
            'message_notes': ''
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            for order in result['data']:
                if 'entrust_no' in order:
                    return int(order['entrust_no'])
        else:
            return self.TRADE_FAIL

    def sh_lof_split(self, code, amount):
        return self._sh_lof_split(1, self.__market_account_sh, code, 1, amount)

    # 上海lof交易: 查询委托
    def _sh_lof_get_entrust_list(self):
        query = {
            'classname': 'com.gf.etrade.control.SHLOFFundControl',
            'method': 'qryAssetSecuprtRealtime'
        }
        payload = {
            'query_type': 1,
            'exchange_type': '',
            'stock_account': '',
            'stock_code': '',
            'serial_no': '',
            'position_str': '',
            'en_entrust_prop': 'LFM,LFP,LFS,LFC,LFR,LFT',
            'request_num': 100,
            'start': 0,
            'limit': 100
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            shlof_entrust_list = list()
            for order in result['data']:
                if 'entrust_no' in order:
                    shlof_entrust_list.append(self.__convert_value_in_dict_to_float(order))
            logging.info('shlof entrust list is: ' + str(shlof_entrust_list))
            return shlof_entrust_list
        else:
            return None

    # @property
    def sh_lof_entrust_list(self):
        return self._sh_lof_get_entrust_list()

    # 上海lof交易: 查询成交
    def _sh_lof_get_trade_list(self):
        query = {
            'classname': 'com.gf.etrade.control.SHLOFFundControl',
            'method': 'qryAssetSecuprtTrade'
        }
        payload = {
            'query_type': 1,
            'query_kind': 0,
            'exchange_type': '',
            'stock_account': '',
            'entrust_no': '',
            'position_str': '',
            'en_entrust_prop': 'LFM,LFP,LFS,LFC,LFR,LFT',
            'request_num': 100,
            'start': 0,
            'limit': 100
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            shlof_trade_list = list()
            for order in result['data']:
                if 'entrust_no' in order:
                    shlof_trade_list.append(self.__convert_value_in_dict_to_float(order))
            logging.info('shlof trade list is: ' + str(shlof_trade_list))
            return shlof_trade_list
        else:
            return None

# sh_lof_trade_list
# {
# 'bond_term': '0',
# 'prop_stock_account': ' ',
# 'position_str': '201509100000011302',
# 'entrust_status_dict': '已成',
# 'prev_balance': '0',
# 'expire_year_rate': '0',
# 'business_amount': 50000.0,
# 'seat_no': '43003',
# 'cbp_business_id': '6000001928',
# 'preterm_year_rate': '0',
# 'entrust_status': '8',
# 'remark': ' ',
# 'entrust_prop_dict': '上证LOF母基金分拆',
# 'prop_branch_no': '0',
# 'client_id': '020290049209',
# 'back_balance': '0',
# 'init_date': '20150910',
# 'join_report_no': '0',
# 'curr_time': '100649',
# 'stock_code': '502006',
# 'exchange_type_dict': '上海',
# 'prop_seat_no': ' ',
# 'fund_account': 'xxxxx',
# 'record_no': '548',
# 'entrust_no': '11302',
# 'curr_date': '20150910',
# 'stock_account': 'xxxxxx',
# 'branch_no': '202',
# 'cbpcontract_id': ' ',
# 'operator_no': ' ',
# 'relation_tel': ' ',
# 'cbpconfer_id': ' ',
# 'entrust_bs': '2',
# 'entrust_amount': 50000.0,
# 'orig_entrust_date': '0',
# 'business_time': '100649',
# 'business_balance': 50000.0,
# 'orig_business_id': ' ',
# 'relation_name': ' ',
# 'exchange_type': '1',
# 'entrust_bs_dict': '卖出',
# 'entrust_type_dict': '委托',
# 'date_back': '0',
# 'op_entrust_way': '7',
# 'stock_name': '国企改革',
# 'entrust_price': '0',
# 'op_station': 'WEB|IP:143.84.63.231,MAC:00:50:56:c0:00:08,HDD:WD-WX31C32M1910,ORIGIN:WEB',
# 'entrust_prop': 'LFP',
# 'entrust_balance': '0',
# 'entrust_type': '0'}
#     @property
    def sh_lof_trade_list(self):
        return self._sh_lof_get_trade_list()

    # 上海lof交易: 撤单
    def sh_lof_cancel(self, entrust_nos):
        query = {
            'classname': 'com.gf.etrade.control.SHLOFFundControl',
            'method': 'secuEntrustWithdraw'
        }
        payload = {
            'entrust_nos': entrust_nos,
            'exchange_types': 1,
            'batch_flag': 0
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            return True
        else:
            return False

    def fund_apply(self, code, amount, market='sh'):
        """
        申购场内基金
        :param code: 代码
        :type code: str
        :param amount: 数量
        :type amount: int
        :param market: 市场, 'sh'为上海; 'sz'为深圳
        :type market: str
        :return: 委托号, -1表示失败
        :rtype: int
        """
        if market.lower() == 'sh':
            return self._fund_apply_redeem(exchange_type=1, stock_code=code, amount=amount, apply_or_redeem=1)
        elif market.lower() == 'sz':
            return self._fund_apply_redeem(exchange_type=2, stock_code=code, amount=amount, apply_or_redeem=1)
        return self.TRADE_FAIL

    def fund_redeem(self, code, amount, market='sh'):
        """
        赎回场外基金
        :param code: 代码
        :type code: str
        :param amount: 数量
        :type amount: int
        :param market: 市场, 'sh'为上海; 'sz'为深圳
        :type market: str
        :return: 委托号, -1表示失败
        :rtype: int
        """
        if market.lower() == 'sh':
            return self._fund_apply_redeem(exchange_type=1, stock_code=code, amount=amount, apply_or_redeem=2)
        elif market.lower() == 'sz':
            return self._fund_apply_redeem(exchange_type=2, stock_code=code, amount=amount, apply_or_redeem=2)
        return self.TRADE_FAIL

    def _fund_apply_redeem(self, exchange_type, stock_code, amount, apply_or_redeem):
        """
        场内基金申购和赎回函数, 不要直接调用
        :param exchange_type: 交易市场, 1为上海; 2为深圳
        :type exchange_type: int
        :param stock_code: 代码
        :type stock_code: str
        :param amount: 数量
        :type amount: int
        :param apply_or_redeem: 交易类型, 1为申购; 2为赎回
        :type apply_or_redeem: int
        :return: 委托号, -1标识失败
        :rtype: int
        """
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'CNJJSS',
        }
        payload = {
            'stock_code': stock_code,
            'exchange_type': exchange_type,
            'entrust_amount': amount,
            'entrust_bs': apply_or_redeem  # 1为申购, 2为赎回
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            for order in result['data']:
                if 'entrust_no' in order:
                    return int(order['entrust_no'])
        return self.TRADE_FAIL

    # 基金分拆
    def fund_split(self, stock_code, amount):
        """
        场内基金分拆函数(不包括上海lof)
        :param stock_code: 代码
        :type stock_code: str
        :param amount: 数量
        :type amount: int
        :return: 委托号
        :rtype: int, -1表示失败
        """
        query = {}
        payload = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'doSplit',
            'stock_code': stock_code,
            'split_amount': amount
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            for order in result['data']:
                if 'entrust_no' in order:
                    return int(order['entrust_no'])
        else:
            return self.TRADE_FAIL

    # 基金合并
    def fund_merge(self, stock_code, amount):
        """
        场内基金合并函数(不包括上海lof)
        :param stock_code: 代码
        :type stock_code: str
        :param amount: 数量
        :type amount: int
        :return: 委托号
        :rtype: int, -1表示失败
        """
        query = {}
        payload = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'doMerge',
            'stock_code': stock_code,
            'merge_amount': amount
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            for order in result['data']:
                if 'entrust_no' in order:
                    return int(order['entrust_no'])
        else:
            return self.TRADE_FAIL

    # 基金查询可撤单
    def fund_cancel_list(self):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'queryFJJJCD'
        }
        payload = {
            'cancelable': 0,
            'position_str': 0,
            'request_num': 100,
            'start': 0,
            'limit': 100
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            fund_cancel_list = list()
            for order in result['data']:
                if 'entrust_no' in order:
                    fund_cancel_list.append(self.__convert_value_in_dict_to_float(order))
            logging.info('shlof trade list is: ' + str(fund_cancel_list))
            return fund_cancel_list
        else:
            return None

    # 基金查询成交
    def fund_trade_list(self):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'queryFJJJCJ'
        }
        payload = {
            'business_flag': '',
            'stock_code': '',
            'request_num': 100,
            'start': 0,
            'limit': 100
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            fund_trade_list = list()
            for order in result['data']:
                if 'entrust_no' in order:
                    fund_trade_list.append(self.__convert_value_in_dict_to_float(order))
            logging.info('shlof trade list is: ' + str(fund_trade_list))
            return fund_trade_list
        else:
            return None

    # 基金查询委托
    def _fund_entrust_list(self, start_date, end_date):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'queryFJJJWT'
        }
        payload = {
            'ksrq': start_date,
            'jsrq': end_date,
            'cancelable': 0,
            'request_num': 100,
            'start': 0,
            'limit': 100
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            fund_trade_list = list()
            for order in result['data']:
                if 'entrust_no' in order:
                    fund_trade_list.append(self.__convert_value_in_dict_to_float(order))
            logging.info('shlof trade list is: ' + str(fund_trade_list))
            return fund_trade_list
        else:
            return None

    # 基金查询当日委托
    def fund_entrust_list(self):
        date = strftime('%Y%m%d')
        return self._fund_entrust_list(date, date)

    # 基金查询历史委托
    def fund_hist_entrust_list(self, start_date, end_date):
        return self._fund_entrust_list(start_date, end_date)

    # 货币基金相关操作
    # 货币基金申购
    def money_fund_apply(self, code, amount, market='sh'):
        """
        申购货币基金
        :param code: 代码
        :type code: str
        :param amount: 数量
        :type amount: int
        :param market: 市场, 'sh'为上海; 'sz'为深圳
        :type market: str
        :return: 委托号, -1表示失败
        :rtype: int
        """
        if market.lower() == 'sh':
            return self._money_fund_apply_redeem(exchange_type=1, stock_code=code, amount=amount, apply_or_redeem=1)
        elif market.lower() == 'sz':
            return self._money_fund_apply_redeem(exchange_type=2, stock_code=code, amount=amount, apply_or_redeem=1)
        return self.TRADE_FAIL

    # 货币基金赎回
    def money_fund_redeem(self, code, amount, market='sh'):
        """
        赎回场外基金
        :param code: 代码
        :type code: str
        :param amount: 数量
        :type amount: int
        :param market: 市场, 'sh'为上海; 'sz'为深圳
        :type market: str
        :return: 委托号, -1表示失败
        :rtype: int
        """
        if market.lower() == 'sh':
            return self._money_fund_apply_redeem(exchange_type=1, stock_code=code, amount=amount, apply_or_redeem=2)
        elif market.lower() == 'sz':
            return self._money_fund_apply_redeem(exchange_type=2, stock_code=code, amount=amount, apply_or_redeem=2)
        return self.TRADE_FAIL

    # 货币基金申赎
    def _money_fund_apply_redeem(self, exchange_type, stock_code, amount, apply_or_redeem):
        """
        货币基金申购和赎回函数, 不要直接调用
        :param exchange_type: 交易市场, 1为上海; 2为深圳
        :type exchange_type: int
        :param stock_code: 代码
        :type stock_code: str
        :param amount: 数量
        :type amount: int
        :param apply_or_redeem: 交易类型, 1为申购; 2为赎回
        :type apply_or_redeem: int
        :return: 委托号, -1标识失败
        :rtype: int
        """
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'HBJJSS',
        }
        payload = {
            'stock_code': stock_code,
            'exchange_type': exchange_type,
            'entrust_amount': amount,
            'entrust_bs': apply_or_redeem  # 1为申购, 2为赎回
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            for order in result['data']:
                if 'entrust_no' in order:
                    return int(order['entrust_no'])
        return self.TRADE_FAIL

    # 货币基金查委托
    def _money_fund_entrust_list(self):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'HBJJWTCX'
        }
        payload = {
            'request_num': 100,
            'position_str': '',
            'start': 0,
            'limit': 100
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            fund_trade_list = list()
            for order in result['data']:
                if 'entrust_no' in order:
                    fund_trade_list.append(self.__convert_value_in_dict_to_float(order))
            logging.info('shlof trade list is: ' + str(fund_trade_list))
            return fund_trade_list
        else:
            return None

    # 货币基金查询当日委托
    def money_fund_entrust_list(self):
        return self.money_fund_apply()

    # 货币基金撤单
    def money_fund_cancel(self, code, entrust_nos, market='sh'):
        if market.lower() == 'sh':
            return self.money_fund_cancel(entrust_nos, 1, code)
        elif market.lower() == 'sz':
            return self.money_fund_cancel(entrust_nos, 2, code)
        return self.TRADE_FAIL

    def _money_fund_cancel(self, entrust_nos, exchange_types, stock_codes):
        query = {
            'classname': 'com.gf.etrade.control.StockUF2Control',
            'method': 'HBJJCD'
        }
        payload = {
            'entrust_nos': entrust_nos,
            'exchange_types': exchange_types,
            'stock_codes': stock_codes,
            'batch_flag': 0
        }
        result = self.__connect_trade_server(query, payload)
        if result:
            return True
        else:
            return False

    # 买入函数,对_buy函数的封装,只需要指定市场,而不需要指定股票账号
    # 市场可选为'sh' 和 'sz' ,默认 'sh'
    def buy(self, code, amount, price, market='sh'):
        if market.lower() == 'sh' and self.__market_account_sh:
            return self._buy(account=self.__market_account_sh, exchange_type=1, code=code, amount=amount, price=price)
        if market.lower() == 'sz' and self.__market_account_sz:
            return self._buy(account=self.__market_account_sz, exchange_type=2, code=code, amount=amount, price=price)
        return self.TRADE_FAIL

    # 卖出函数,对_sell函数的封装,只需要指定市场,而不需要指定股票账号
    # 市场可选为'sh' 和 'sz' ,默认 'sh'
    def sell(self, code, amount, price, market='sh'):
        if market.lower() == 'sh' and self.__market_account_sh:
            return self._sell(account=self.__market_account_sh, exchange_type=1, code=code, amount=amount, price=price)
        if market.lower() == 'sz' and self.__market_account_sz:
            return self._sell(account=self.__market_account_sz, exchange_type=2, code=code, amount=amount, price=price)
        return self.TRADE_FAIL

    def cancel_all(self):
        return self._cancel_all()

    def cancel_buy(self):
        return self._cancel_all(direction='buy')

    def cancel_sell(self):
        return self._cancel_all(direction='sell')

if __name__ == '__main__':
    # logging.info("This is a test......\n")
    config = dict()
    with open('../Configs/Socket.config.gf', 'r') as f:
        config = json.loads(f.read().replace(r'\n', ''))
    gf = GFSocket(config['account'], config['password'])
    gf.prepare_login()
    gf.show_verify_code()
    vericode = input("input verify code:")
    gf.enter_verify_code(vericode)
    gf.login()
    gf.prepare_trade()
    print(str(gf.stock_position))
    print(str(gf.entrust_list))
    print(str(gf.trade_list))
    print(str(gf.cancel_list))
    print(str(gf.sh_lof_trade_list))

    gf.logout()
