#
# Created by 'changye'  on '15-9-1'
# 邮件通知系统
#

__author__ = 'changye'
import smtplib
import poplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.encoders import encode_base64
from email.mime.base import MIMEBase
from email.header import Header, decode_header
from email.utils import parseaddr, formataddr
from email.parser import Parser
import logging
logging.basicConfig(level=logging.WARNING)


def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].strip()
    return charset


class Notifier(object):
    def __init__(self, from_email, password, to_mail=None, smtp_server=None, pop_server=None):
        self.__from = from_email
        self.__password = password
        self.__smtp_server = smtp_server
        self.__pop_server = pop_server

        if to_mail is not None and type(to_mail) is not list:
            self.__to = [to_mail]
        else:
            self.__to = to_mail

    def send(self, subject, content, to=None, image=None):
        server = smtplib.SMTP(self.__smtp_server, 25)
        server.set_debuglevel(1)
        to_list = list()
        if to is not None:
            if type(to) is list:
                to_list = to
            else:
                to_list.append(to)
        elif self.__to is not None:
            to_list = self.__to
        else:
            return False

        server.login(self.__from, self.__password)
        msg = MIMEMultipart()
        msg['From'] = _format_addr('<%s>' % self.__from)
        msg['To'] = _format_addr('<%s>' % ','.join(to_list))
        msg['Subject'] = Header(subject, 'utf-8').encode()
        # msg.attach(MIMEText(content, 'plain', 'utf-8'))
        msg.attach(MIMEText(content, 'html', 'utf-8'))

        if image is not None:
            with open(image, 'rb') as f:
                mime = MIMEBase('image', 'png', filename='image.png')
                # 把附件的内容读进来:
                mime.set_payload(f.read())
                # 用Base64编码:
                encode_base64(mime)
                # 加上必要的头信息:
                mime.add_header('Content-Disposition', 'attachment', filename='image.png')
                mime.add_header('Content-ID', '<0>')
                mime.add_header('X-Attachment-Id', '0')
                # 添加到MIMEMultipart:
                msg.attach(mime)
        server.sendmail(self.__from, to_list, msg.as_string())
        server.quit()
        return True

    def receive(self, subject):
        server = poplib.POP3(self.__pop_server)
        server.set_debuglevel(1)
        server.user(self.__from)
        server.pass_(self.__password)
        resp, mails, octets = server.list()

        import re
        mail_number = len(mails)
        for i in range(mail_number, 0, -1):
            resp, lines, octets = server.retr(i)

            # 可以获得整个邮件的原始文本:
            msg_content = b'\r\n'.join(lines).decode('utf-8')
            # 稍后解析出邮件:
            msg = Parser().parsestr(msg_content)
            msg_subject, charset = decode_header(msg.get('Subject', ''))[0]
            if type(msg_subject) is not str:
                msg_subject = msg_subject.decode(charset)
            # logging.warning(msg_subject)
            if msg_subject and msg_subject.find(subject) >= 0:
                content_type = msg.get_content_type()
                if content_type == 'text/plain' or content_type == 'text/html':
                    content = msg.get_payload(decode=True)
                    charset = guess_charset(msg)
                    content = content.decode(charset)
                    return content
                if content_type == 'multipart/alternative':
                    parts = msg.get_payload()
                    for p in parts:
                        if p.get_content_type() == 'text/plain' or p.get_content_type() == 'text/html':
                            content = p.get_payload(decode=True)
                            charset = guess_charset(p)
                            content = content.decode(charset)
                            return content
                return None
        return None

