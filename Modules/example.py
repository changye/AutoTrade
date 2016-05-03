from Modules.Module import Module
from datetime import timedelta
from Trade.Job import Job
from Trade.Job import Dependence

#
# Created by 'changye'  on '15-11-18'
#

__author__ = 'changye'


class Example(Module):
    def __init__(self, config):
        super().__init__()

        # 对Module初始化操作
        import os
        if not config or not os.path.isfile(config):
            self.__config = None
            raise FileNotFoundError
        else:
            self.__config = config

        self.__error = False

        # 用户在此处添加自定义的Module初始化


    def prepare(self, module_no):
        super().prepare(module_no)
        # 用户在此处进行Module的准备工作, 包括读取配置文件, 准备关注标的物信息等


    def focus_list(self):

        # 用户在此处将需要关注的标的物加入列表,并返回
        # 如果没有任何关注标的,返回空列表
        # 例子:
        # return ['sh600004, sh600036, sz000002']

        return []

    def need_to_trade(self, quotes, time_stamp):
        super().need_to_trade(quotes, time_stamp)
        if self.__error:
            return None

        # 用户策略在这里加入, 本函数会被系统反复调用, 本函数的输入共两个,
        # 其中quotes为关注的标的物的报价信息.
        # time_stamp为时间戳, 类行为datatime

        # 交易下单过程
        # 1.声明一个队列存放交易单
        # jobs = list()

        # 买入
        # job1 = self.create_new_job(time_stamp)\
        #     .set(Job.BUY, '600004', 'sh', 10000, 12.8)\
        #     .set_message('买入 %s %d @ $%.3f' % ('600004', 'sh', 10000, 12.8))
        # jobs.append(job1)

        # 卖出
        # job2 = self.create_new_job(time_stamp)\
        #     .set(Job.SELL, '600004', 'sh', 10000, 12.8)\
        #     .set_message('买入 %s %d @ $%.3f' % ('600004', 'sh', 10000, 12.8))
        # jobs.append(job2)

        # 存在依赖关系的交易
        # 下面的例子提交了一个交易指令: 当job1成交后再执行买入操作
        # job3 = self.create_new_job(time_stamp)\
        #     .set(Job.SELL, '600004', 'sh', 10000, 12.8)\
        #     .set_message('买入 %s %d @ $%.3f' % ('600014', 'sh', 10000, 15))
        # job3.add_dependence(Dependence(job1, Job.TRADED_ALL))
        # jobs.append(job3)

        # 注意: jobs.append(XX) 仅仅是将XX交易添加到交易列表, \
        # 只有当本函数返回的时候, 所有的交易指令才会一并提交给交易系统执行.
        # 执行的先后顺序按照先入先出的规律, 存在依赖关系的交易除外
        # return jobs

        # 如果不需要任何交易, 返回空列表
        return []



