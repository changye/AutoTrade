#
# Created by 'changye'  on '15-11-2'
#

__author__ = 'changye'


class Dependence(object):
    # 已死亡, 若B依赖于A, A死亡则B死亡
    DEAD = -1
    # 依赖关系尚未满足, 等待
    WAIT = 0
    # 依赖关系已经实现, 可以发射
    READY = 1

    def __init__(self, depend_job, status):
        self.__depend_job_module_no = depend_job.module_no
        self.__depend_job_serial_no = depend_job.serial_no
        self.__depend_job_status = status

    @property
    def depend_job_module_no(self):
        return self.__depend_job_module_no

    @property
    def depend_job_serial_no(self):
        return self.__depend_job_serial_no

    @property
    def depend_job_status(self):
        return self.__depend_job_status

    @property
    def depend_job(self):
        return self.__depend_job_module_no, self.depend_job_serial_no, self.depend_job_status


class Job(object):

    NONE = 0
    BUY = 1
    SELL = 2
    CANCEL = 3

    FUND_APPLY = 11
    FUND_REDEEM = 12
    FUND_SPLIT = 13
    FUND_MERGE = 14

    # 每一个job的状态
    # 尝试次数已经超过限额
    DEAD = -4
    # 失败
    FAILED = -3
    # 已撤单
    CANCELED = -2
    # 已撤单, 但部分已经成交
    CANCELED_PARTLY = -1
    # 挂起, 表示等待执行中
    PENDING = 0
    # 已委托
    ENTRUSTED = 1
    # 收市后成交
    TRADE_AFTER_MARKET_CLOSE = 2
    # 部分成交
    TRADED_PARTLY = 3
    # 全部成交
    TRADED_ALL = 4

    def __init__(self, module_no, serial_no, time_stamp):
        self.__module_no = module_no
        self.__serial_no = serial_no
        # 委托号
        self.__entrust_no = -1
        # 状态位
        self.__status = self.PENDING
        # 最大重试次数
        self.__allow_retry_times = 3
        # 已经尝试的次数
        self.__tried_times = 0
        # 委托的依赖条件
        self.__dependence = list()
        # 委托的操作
        self.__action = self.NONE
        # 委托代码
        self.__code = None
        # 委托的市场
        self.__market = None
        # 委托数量
        self.__amount = 0
        # 委托价格
        self.__price = 0
        # 需要撤单的序列号, 撤单时使用
        self.__cancel_serial_no = -1
        # 时间戳
        self.__time_stamp = time_stamp
        # 附加信息
        self.__msg = ''
        # 模拟发射
        self.__simulate = False

    def set(self, action, code, market, amount, price, depend=None, msg='', cancel_job=None):
        # 如果是撤单的话,需要entrust_no大于0
        if action == Job.CANCEL:
            if cancel_job is not None and isinstance(cancel_job, Job):
                self.__action = Job.CANCEL
                self.__cancel_serial_no = cancel_job.serial_no
                self.add_dependence(depend)
        else:
            self.__action = action
            self.__code = code
            self.__market = market
            self.__amount = amount
            self.__price = price
            self.__msg = msg
            self.add_dependence(depend)
        return self

    def set_cancel(self, job):
        self.__action = self.CANCEL
        self.__cancel_serial_no = job.serial_no
        return self

    def set_message(self, msg):
        self.__msg = msg
        return self

    def set_none(self):
        self.__action = self.NONE
        self.__status = self.CANCELED
        return self

    def set_simulate(self, simulate):
        self.__simulate = simulate
        return self

    def get_cancel_serial_no(self):
        return self.__cancel_serial_no

    def add_dependence(self, depend):
        if depend is not None and isinstance(depend, Dependence):
            self.__dependence.append(depend)

    @property
    def action(self):
        return self.__action

    @property
    def action_detail(self):
        return self.__market, self.__code, self.__amount, self.__price

    @property
    def dependence(self):
        return self.__dependence

    @property
    def status(self):
        return self.__status

    @status.setter
    def status(self, value):
        if Job.DEAD <= value <= Job.TRADED_ALL:
            self.__status = value

    @property
    def entrust_no(self):
        return self.__entrust_no

    @entrust_no.setter
    def entrust_no(self, value):
        if type(value) is int:
            self.__entrust_no = value

    @property
    def is_simulate(self):
        return self.__simulate

    @property
    def module_no(self):
        return self.__module_no

    @property
    def serial_no(self):
        return self.__serial_no

    @property
    def tried_times(self):
        return self.__tried_times

    def tried_once(self):
        self.__tried_times += 1

    @property
    def allow_retry_times(self):
        return self.__allow_retry_times

    def set_allow_retry_times(self, value):
        if type(value) is int and value > 0:
            self.__allow_retry_times = value

    def mark_dead(self):
        self.__status = Job.DEAD

    def mark_entrust(self, entrust_no):
        self.entrust_no = entrust_no
        self.status = Job.ENTRUSTED

    def mark_fail(self):
        self.__status = Job.FAILED

    def mark_trade_after_market_close(self):
        self.__status = Job.TRADE_AFTER_MARKET_CLOSE

    def mark_traded_all(self):
        self.__status = Job.TRADED_ALL

    def mark_traded_partly(self):
        self.__status = Job.TRADED_PARTLY

    @property
    def already_entrusted(self):
        return self.status > Job.PENDING

    @property
    def exceed_allow_retry_times(self):
        return self.tried_times >= self.allow_retry_times

    @property
    def is_none(self):
        return self.action == Job.NONE

    @property
    def is_dead(self):
        return self.status == Job.DEAD

    @property
    def is_pending(self):
        return self.status == Job.PENDING

    @property
    def is_failed(self):
        return self.status == Job.FAILED

    @property
    def is_canceled(self):
        return self.status == Job.CANCELED or self.status == Job.CANCELED_PARTLY

    @property
    def need_to_issue(self):
        return self.status == Job.PENDING or self.status == Job.FAILED

    @property
    def need_to_review(self):
        return self.status == Job.ENTRUSTED or self.status == Job.TRADED_PARTLY

    @property
    def info(self):
        result = ''
        if self.__action == self.NONE:
            result = '[%d:%d] %s(%s)\nMSG:%s' % \
                     (self.__module_no, self.__serial_no,
                      'Nothing need to be done!', self.__code, self.__msg)
        if self.__action == self.BUY:
            result = '[%d:%d] %s %d of \'%s\' @ price $%.3f\nMSG:%s' \
                     % (self.__module_no, self.__serial_no,
                        'Buy', self.__amount, self.__code, self.__price, self.__msg)
        elif self.__action == self.SELL:
            result = '[%d:%d] %s %d of \'%s\' @ price $%.3f\nMSG:%s' \
                     % (self.__module_no, self.__serial_no,
                        'Sell', self.__amount, self.__code, self.__price, self.__msg)
        elif self.__action == self.CANCEL:
            result = '[%d:%d] %s job(serial no: %s)\nMSG:%s' \
                     % (self.__module_no, self.__serial_no,
                        'Canceling', self.__entrust_no, self.__cancel_serial_no)

        elif self.__action == self.FUND_APPLY:
            result = '[%d:%d] %s %d of \'%s\' @ %.3f(estimate)\nMSG:%s' \
                     % (self.__module_no, self.__serial_no,
                        'Apply', self.__amount, self.__code, self.__price, self.__msg)
        elif self.__action == self.FUND_REDEEM:
            result = '[%d:%d] %s %d of \'%s\' # %.3f(estimate) \nMSG:%s' \
                     % (self.__module_no, self.__serial_no,
                        'Redeem', self.__amount, self.__code, self.__price, self.__msg)

        return result


