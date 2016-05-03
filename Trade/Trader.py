from Socket.GFSocket import GFSocket
from multiprocessing import Process, Lock, Value, Manager
from multiprocessing.managers import BaseManager
from time import sleep
from Trade.Job import Job, Dependence
import logging

#
# Created by 'changye'  on '15-11-5'
#

__author__ = 'changye'


class MyManager(BaseManager):
    pass

def SocketManager():
    m = MyManager()
    m.start()
    return m

MyManager.register('GFSocket', GFSocket)


class Trader(object):
    def __init__(self, account, password, notifier, ocr_service, debug_single_step=False):
        self.__account = account
        self.__password = password
        self.__notifier = notifier
        self.__ocr_service = ocr_service

        self.__manager = Manager()

        self.__job_list = self.__manager.list()
        self.__job_list_lock = Lock()

        self.__map = self.__manager.dict()
        self.__entrust_map = self.__manager.dict()

        self.__process = None
        self.__keep_working = Value('i', 1)

        if debug_single_step:
            self.__debug_single_step = Value('i', 1)
        else:
            self.__debug_single_step = Value('i', 0)

        self.__debug_single_step_go = Value('i', 0)
        self.__debug_single_step_lock = Lock()

    def initial_socket(self):
        socket_manager = SocketManager()
        self.__socket = socket_manager.GFSocket(self.__account, self.__password)
        
    def sign_in_socket(self, retry_times=5, fetch_vericode_inteval=60, fetch_vericode_times=3):
        # import random
        # import string
        # from time import sleep
        # import re
        counter = 0
        while counter < retry_times:
            # 获取验证码
            verify_code = self.__socket.prepare_login()
            verify_code = self.__ocr_service.recognize(verify_code, self.__socket.verify_code_length())
            if verify_code is None:
                continue
            logging.info('verify_code is %s' % (verify_code, ))
            self.__socket.enter_verify_code(verify_code)
            if self.__socket.login() is True:
                self.__socket.prepare_trade()
                return True
            counter += 1
            sleep(fetch_vericode_inteval)
        return False

    def sign_out_socket(self):
        self.__socket.logout()

    def add_jobs_to_pending_list(self, jobs):
        self.__job_list_lock.acquire()
        logging.info('add jobs to job_list')
        start_index = len(self.__job_list)
        for j in jobs:
            self.__job_list.append(j)

            # 将job的位置加入查找表之中
            # logging.warning('add job to map %d,%d,%d' % (j.module_no, j.serial_no, start_index))
            self.job_map(j.module_no, j.serial_no, start_index)
            start_index += 1
        logging.info('release job_list')
        self.__job_list_lock.release()

    def job_map(self, module_no, serial_no, index):
        key = '%d-%d' % (module_no, serial_no)
        self.__map[key] = index

    def job_find(self, module_no, serial_no):
        key = '%d-%d' % (module_no, serial_no)
        index = self.__map.get(key, -1)
        # logging.warning('find %d,%d,%d' % (module_no, serial_no, index))
        return index

    def start(self):
        self.__process = Process(target=self.__issue_cmd)
        self.__process.start()

    def exit(self):
        self.__keep_working.value = 0
        self.__process.join()

    def __issue_cmd(self):
        start_issue_index = 0
        start_review_index = 0

        while self.__keep_working.value == 1:
            # 如果处于单步测试模式, 则只有single_step_go不为0时才能继续运行
            if self.__debug_single_step.value == 1:
                if self.__debug_single_step_go.value == 0:
                    continue
                else:
                    self.__debug_single_step_lock.acquire()
                    self.__debug_single_step_go.value = 0
                    self.__debug_single_step_lock.release()

            # 发射交易命令
            # 获得job_list的锁, 以防止在查询job_list长度的时候 job_list加入新的命令
            self.__job_list_lock.acquire()
            last_job_index = len(self.__job_list)
            # 释放锁
            self.__job_list_lock.release()
            # logging.warning('start is %d' % (start_issue_index, ))
            pass
            # 开始发射指令
            for index in range(start_issue_index, last_job_index):
                self._do_issue(index)

            # 查找下一次发射的起始值 以及下一次review的起始值
            start_search_index = min(start_issue_index, start_review_index)
            for index in range(start_search_index, last_job_index):
                job = self.__job_list[index]
                # 下一次发射的起始值确定的条件：
                # 在第0条指令到下一次发射的起始值之间(不含下一次发射的起始值)， 所有的job必须need_to_issue为False
                if not job.need_to_issue:
                    if start_issue_index == index:
                        start_issue_index = index + 1
                # 下一次review起始值确定条件:
                # 在第0条指令到下一次review的起始值间(不含下一次review的起始值), 所有的job必须need_to_review为False
                if not job.need_to_review:
                    if start_review_index == index:
                        start_review_index = index + 1

            # 如果start_review_index大于等于job_list的长度,说明所有的Job都不需要更新状态
            # 否则说明存在已委托但未成交或未撤单的指令,这些指令需要定期访问券商以更新他们的状态
            # print('start issue index is %d, and start review index is %d' % (start_issue_index, start_review_index))
            if start_review_index < last_job_index:
                sleep(0.5)
                self.refresh_job_status()

    def _do_issue(self, index):
        job = self.__job_list[index]
        ready_to_issue = True
        need_to_write_back = False
        logging.warning('issuing job[%d:%d]' % (job.module_no, job.serial_no))
        # 查看job是否为simulate job, 如果是则进打印job的msg, 如果否才是真正需要发射的job
        if job.is_simulate is True:
            logging.warning('[Simulate]\t%s' % (job.info,))
            job.mark_dead()
            self.__job_list_lock.acquire()
            self.__job_list[index] = job
            self.__job_list_lock.release()
            return

        # 查看job是否需要发射, 已经发射过的以及已经死亡的job都不需要发射
        if not job.need_to_issue:
            logging.warning('已经发射过了,已经成交了或者已经死亡了')
            return

        # 查看job是否已经超过了允许发送的次数
        if job.exceed_allow_retry_times:
            logging.warning('发射次数超过了%d次' % (job.allow_retry_times, ))
            job.mark_dead()
            need_to_write_back = True
            ready_to_issue = False

        # 查看job的依赖条件是否满足
        if ready_to_issue:
            for d in job.dependence:
                one_dependence_ready = self.check_depend(d)
                if one_dependence_ready == Dependence.WAIT:
                    ready_to_issue = False
                elif one_dependence_ready == Dependence.DEAD:
                    # 如果发现依赖的job已经死亡,则本job也标记为死亡
                    job.mark_dead()
                    need_to_write_back = True
                    ready_to_issue = False
                    break

        # 满足发射的条件,则发出交易指令
        if ready_to_issue:
            # 具体的发射指令
            self.__do_issue(index, job)
            sleep(0.05)
            need_to_write_back = True
            logging.info(job.info)

        # 下面非常重要, 如果job的状态发生了变化,需要将job拷贝回list中,否则list中的内容是不会改变的
        if need_to_write_back:
            self.__job_list_lock.acquire()
            self.__job_list[index] = job
            self.__job_list_lock.release()

    def check_depend(self, depend):
        """
        查询Job的依赖关系是否实现
        :param depend: 依赖条件
        :type depend: Trade.Job.Dependence
        :return:
        """
        index = self.job_find(depend.depend_job_module_no, depend.depend_job_serial_no)
        job = self.__job_list[index]
        if job.status >= depend.depend_job_status:
            return Dependence.READY
        elif job.status == Job.DEAD:
            return Dependence.DEAD
        else:
            return Dependence.WAIT

    def __do_issue(self, index, job):
        """
        具体的交易发射在这里实现
        :param index: 发射的指令在self.__job_list中的位置
        :type index: int
        :param job: 发射的命令
        :type job: Trade.Job.Job
        :return:
        :rtype:
        """
        # 发射次数加1
        job.tried_once()
        (market, code, amount, price) = job.action_detail

        # 买入操作
        if job.action == Job.BUY:
            entrust_no = self.__socket.buy(code, amount, price, market=market)
            if entrust_no >= 0:
                job.mark_entrust(entrust_no)
                self.__entrust_map[entrust_no] = index
            else:
                job.mark_fail()
            return

        # 卖出操作
        if job.action == Job.SELL:
            entrust_no = self.__socket.sell(code, amount, price, market=market)
            if entrust_no >= 0:
                job.mark_entrust(entrust_no)
                self.__entrust_map[entrust_no] = index
            else:
                job.mark_fail()
            return

        # 撤单操作
        if job.action == Job.CANCEL:
            job_need_to_cancel_index = self.job_find(job.module_no, job.get_cancel_serial_no())
            if job_need_to_cancel_index != -1:
                job_need_to_cancel = self.__job_list[job_need_to_cancel_index]
                if job_need_to_cancel.entrust_no >= 0 and Job.PENDING < job_need_to_cancel.status < Job.TRADED_ALL:
                    result = self.__socket.cancel(job_need_to_cancel.entrust_no)
                    if result is True:
                        job.mark_traded_all()
                    else:
                        job.mark_fail()
                else:
                    job.mark_fail()
            else:
                job.mark_dead()
            return

        # 场内基金申赎及分拆合并操作(不包括上海lof基金)
        if job.action == Job.FUND_APPLY:
            entrust_no = self.__socket.fund_apply(code, amount, market)
            if entrust_no >= 0:
                job.mark_entrust(entrust_no)
                job.mark_trade_after_market_close()
                self.__entrust_map[entrust_no] = index
            else:
                job.mark_fail()
            return

        if job.action == Job.FUND_REDEEM:
            entrust_no = self.__socket.fund_redeem(code, amount, market)
            if entrust_no >= 0:
                job.mark_entrust(entrust_no)
                job.mark_trade_after_market_close()
                self.__entrust_map[entrust_no] = index
            else:
                job.mark_fail()
            return

        if job.action == Job.FUND_SPLIT:
            entrust_no = self.__socket.fund_split(code, amount)
            if entrust_no >= 0:
                job.mark_entrust(entrust_no)
                job.mark_trade_after_market_close()
                self.__entrust_map[entrust_no] = index
            else:
                job.mark_fail()
            return

        if job.action == Job.FUND_MERGE:
            entrust_no = self.__socket.fund_merge(code, amount)
            if entrust_no >= 0:
                job.mark_entrust(entrust_no)
                job.mark_trade_after_market_close()
                self.__entrust_map[entrust_no] = index
            else:
                job.mark_fail()
            return

        # 如果如不在上述操作实现的范围内,说明该操作不存在或尚未实现,该任务认为是死任务
        job.mark_dead()
        return

    def refresh_job_status(self):
        entrusted_jobs = self.__socket.entrust_list()
        for j in entrusted_jobs:
            # Socket返回的值是字符串,而trader存入的值是一个数字,这个地方需要特别注意
            entrust_no = j['entrust_no']
            job_status = self.entrust_status_to_job_status(j['entrust_status'], j['entrust_status_dict'])
            index = self.__entrust_map.get(entrust_no, -1)
            # print(entrust_no, index, job_status)
            if index >= 0:
                job = self.__job_list[index]
                # 无变化则不需要更新
                if job.status == job_status:
                    continue
                # 如果是收盘后才能成交的交易(例如深市分级基金的申购,在收市之前始终处于已报状态)
                # 在这种情况下, 已报状态即等价为TRADE_AFTER_MARKET_CLOSE
                elif job.status == Job.TRADE_AFTER_MARKET_CLOSE and job_status == Job.ENTRUSTED:
                    continue
                else:
                    # print(index, job_status)
                    job.status = job_status
                    self.__job_list_lock.acquire()
                    self.__job_list[index] = job
                    self.__job_list_lock.release()
            else:
                continue

    @staticmethod
    def entrust_status_to_job_status(entrust_status, entrust_status_dict):
        """
        将券商的entrust_status映射到Job类的Job.status
        :param entrust_status: 券商返回的委托状态,8为已成,9为废单,6为已撤,2为已报,7为部成,5为部撤,3为已报待撤
        :type entrust_status: int
        :return: Job类的状态
        :rtype: int
        """
        if entrust_status == 2 or entrust_status == 3:
            return Job.ENTRUSTED

        if entrust_status == 5:
            return Job.CANCELED_PARTLY

        if entrust_status == 6:
            return Job.CANCELED

        if entrust_status == 9:
            return Job.DEAD

        if entrust_status == 7:
            return Job.TRADED_PARTLY

        if entrust_status == 8:
            return Job.TRADED_ALL

        logging.error('ERROR!!\t返回委托状态: %d (%s) 未知, 请确认!!' % (entrust_status, entrust_status_dict))
        # 该返回值需要再考虑,如果券商返回了一个未知的值,如何避免出现误操作.
        return Job.ENTRUSTED

    def get_stock_position(self, force_refresh=False):
        """
        获取股票持仓
        :param force_refresh: 强制刷新,暂未开放,默认既为强制刷新
        :type force_refresh: bool
        :return: 返回股票持仓
        :rtype: list
        """
        return self.__socket.stock_position()

    def get_balance(self, force_refresh=False):
        """
        获取资金账户信息
        :param force_refresh: 强制刷新,暂未开放,默认既为强制刷新
        :type force_refresh: bool
        :return: 返回股票持仓
        :rtype: list
        """
        return self.__socket.balance()

    def check_job_status(self, job):
        index = self.job_find(job.module_no, job.serial_no)
        try:
            return self.__job_list[index].status
        except IndexError:
            return Job.DEAD

    def debug_single_step_go(self):
        self.__debug_single_step_lock.acquire()
        self.__debug_single_step_go.value = 1
        self.__debug_single_step_lock.release()

if __name__ == '__main__':

    import json
    # 配置校验码识别系统的用户名和密码(校验码识别由ruokuai.com提供, 请注册该网站的用户(非开发者))
    config_ocr = dict()
    with open('../Configs/Tools.config.ocr', 'r') as f:
        config_ocr = json.loads(f.read().replace(r'\n', ''))
    from Tools.Ocr import Ocr
    my_ocr = Ocr(config_ocr['account'], config_ocr['password'])

    config = dict()
    with open('../Configs/Socket.config.gf', 'r') as f:
        config = json.loads(f.read().replace(r'\n', ''))
    trader = Trader(config['account'], config['password'], notifier=notifier, ocr_service=ocr)

    trader.initial_socket()
    trader.sign_in_socket()
    print(trader.get_stock_position())
    print(trader.get_balance())



