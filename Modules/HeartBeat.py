#
# Created by 'changye'  on '15-10-30'
#

__author__ = 'changye'

from Modules.Module import Module
from datetime import timedelta
from Trade.Job import Job
import logging


class HeartBeat(Module):

    def __init__(self, heart_beat_interval_in_minutes=5):
        super().__init__()
        self.__heart_beat_interval = heart_beat_interval_in_minutes
        self.__last_heart_beat_time = None
        # self._last_job = None

    def prepare(self, module_no):
        super().prepare(module_no)

    def focus_list(self):
        return []

    def need_to_trade(self, quotes, time_stamp):
        super().need_to_trade(quotes, time_stamp)

        if self.__last_heart_beat_time is None \
                or self.__last_heart_beat_time + timedelta(minutes=self.__heart_beat_interval) < time_stamp:
            self.get_balance(force_refresh=True)
            self.__last_heart_beat_time = time_stamp
            logging.info('Heartbeat! [%s]' % (time_stamp.strftime('%H:%M:%S')))
            # if self._last_job is None or self._last_job.action == Job.CANCEL:
            #     job = self.create_new_job(time_stamp).set(Job.BUY, '511990', 'sh', 100, 99.9, msg='下单购买511990')
            # else:
            #     job = self.create_new_job(time_stamp).set_cancel(self._last_job).set_message('撤单!')
            # self._last_job = job
            # return [job]

        return None



