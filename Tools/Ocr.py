#!/usr/bin/env python
# coding:utf-8

import requests
from hashlib import md5


class RClient(object):

    def __init__(self, username, password, soft_id, soft_key):
        self.username = username
        self.password = md5(password.encode('utf8')).hexdigest()
        self.soft_id = soft_id
        self.soft_key = soft_key
        self.base_params = {
            'username': self.username,
            'password': self.password,
            'softid': self.soft_id,
            'softkey': self.soft_key,
        }
        self.headers = {
            'Connection': 'Keep-Alive',
            'Expect': '100-continue',
            'User-Agent': 'ben',
        }

    def rk_create(self, im, im_type, timeout=60):
        """
        im: 图片字节
        im_type: 题目类型
        """
        params = {
            'typeid': im_type,
            'timeout': timeout,
        }
        params.update(self.base_params)
        files = {'image': ('a.jpg', im)}
        r = requests.post('http://api.ruokuai.com/create.json', data=params, files=files, headers=self.headers)
        return r.json()

    def rk_report_error(self, im_id):
        """
        im_id:报错题目的ID
        """
        params = {
            'id': im_id,
        }
        params.update(self.base_params)
        r = requests.post('http://api.ruokuai.com/reporterror.json', data=params, headers=self.headers)
        return r.json()


# 使用www.ruokuai.com提供的服务
class Ocr(RClient):

    def __init__(self, username, password):
        super().__init__(username, password, soft_id='46690', soft_key='8b2cb811991046d59c742040a7c18d7f')
        self.__last_ocr = None

    def recognize(self, image_file, vericode_length):
        mode = 5000  # 任意长度中英文数字
        if type(vericode_length) is int and vericode_length > 0:
            mode = 3000 + vericode_length * 10  # 特定长度英文+数字
        import os
        if os.path.isfile(image_file):
            im = open(image_file, 'rb').read()
        self.__last_ocr = self.rk_create(im, mode)

        if 'Result' not in self.__last_ocr:
            if 'Error' in self.__last_ocr:
                print(self.__last_ocr['Error'])
            return None

        if 0 < vericode_length != len(self.__last_ocr['Result']):
            self.rk_report_error(self.__last_ocr['Id'])
            return None
        else:
            return self.__last_ocr['Result']

    def report_error(self):
        self.rk_report_error(self.__last_ocr['Id'])


if __name__ == '__main__':
    ocr = Ocr('changye', '19820928')
    result = ocr.recognize('../vericode.jpeg', 5)
    print(result)

