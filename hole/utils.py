from django.core.mail import send_mail
from smtplib import SMTPException
import logging, random

def mail(recipient, code, mode='register'):
    domain = 'http://127.0.0.1:8000'
    try:
        if mode == 'register':
            send_mail(
                subject='FDUHOLE 注册验证',
                message='欢迎注册 FDUHOLE，请点击以下链接以继续  ' + domain + '/hole/verify/' + code + '\r\n如果您意外地收到了此邮件，请忽略它',
                from_email='fduhole@gmail.com',
                recipient_list=[recipient],
                fail_silently=False,
            )
        if mode == 'change_password':
            send_mail(
                subject='FDUHOLE 修改密码验证',
                message='请点击以下链接以继续  ' + domain + '/hole/verify/' + code + '\r\n如果您意外地收到了此邮件，请忽略它',
                from_email='fduhole@gmail.com',
                recipient_list=[recipient],
                fail_silently=False,
            )
    except SMTPException as e:
        logging.error('SMTP exception')
        logging.error('邮件发送错误，收件人：{}，令牌码：{}，模式：{}，错误信息：{}'.format(recipient, code, mode, e))

def ranstr(num):
    # 猜猜变量名为啥叫 H
    H = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
    salt = ''
    for i in range(num):
        salt += random.choice(H)
    return salt


    # send_mail(
    #             subject='FDUHOLE 注册验证',
    #             message='欢迎注册 FDUHOLE，请点击以下链接以继续 ',
    #             from_email='fduhole@gmail.com',
    #             recipient_list=['20300680017@fudan.edu.cn'],
    #             fail_silently=False,
    #         )