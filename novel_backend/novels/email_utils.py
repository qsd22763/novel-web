"""
墨香书阁 — QQ邮箱SMTP验证码发送工具
使用QQ邮箱第三方授权码发送验证码邮件
"""

import os
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, parseaddr
from email.header import Header


def get_smtp_config():
    """从环境变量读取QQ邮箱SMTP配置"""
    return {
        'smtp_host': os.environ.get('EMAIL_SMTP_HOST', 'smtp.qq.com'),
        'smtp_port': int(os.environ.get('EMAIL_SMTP_PORT', 465)),
        'sender_email': os.environ.get('EMAIL_SENDER', ''),
        'auth_code': os.environ.get('EMAIL_AUTH_CODE', ''),
    }


def send_verification_email(to_email: str, code: str) -> bool:
    """
    通过QQ邮箱SMTP发送验证码邮件

    Args:
        to_email: 收件人邮箱（用户填写的QQ邮箱）
        code: 6位数字验证码

    Returns:
        True 发送成功

    Raises:
        ValueError: 配置缺失或认证/发送失败
    """
    config = get_smtp_config()

    if not config['sender_email']:
        raise ValueError('未配置发件邮箱，请在 .env 中设置 EMAIL_SENDER')
    if not config['auth_code']:
        raise ValueError('未配置授权码，请在 .env 中设置 EMAIL_AUTH_CODE（非QQ密码）')

    # 国风邮件正文模板
    subject = '【墨香书阁】注册验证码'
    body = f"""<div style="font-family: 'Noto Serif SC', 'STSong', SimSun, serif; max-width: 520px; margin: 0 auto; padding: 30px; background: linear-gradient(165deg, #FFFDF9 0%, #FFFCF7 40%, #F7F1E8 100%); border-radius: 16px; border: 1px solid rgba(201,160,74,0.15);">
<div style="text-align: center; padding-bottom: 20px; border-bottom: 2px solid rgba(201,160,74,0.25);">
<h1 style="font-size: 22px; color: #A88532; margin: 0; letter-spacing: 4px;">墨香書閣</h1>
<p style="font-size: 13px; color: #9E8D7A; margin-top: 6px; letter-spacing: 2px;">为阅读而生，为故事而活</p>
</div>

<div style="padding: 24px 16px;">
<p style="font-size: 14.5px; color: #3D332A; line-height: 2; margin-bottom: 8px;">
阁下安好，<br/>
感谢您选择墨香书阁。您的注册验证码如下：
</p>

<div style="background: linear-gradient(135deg, #4A3C30 0%, #735B3E 35%, #A88532 70%, #DDB96B 100%);
border-radius: 12px; padding: 18px 24px; text-align: center; margin: 20px 0;
box-shadow: inset 0 1.5px 0 rgba(255,255,255,0.14), 0 4px 14px rgba(74,60,48,0.22);">
<span style="font-family: 'Noto Serif SC', serif; font-size: 32px; font-weight: 700; color: #FFFBF5; letter-spacing: 10px; text-shadow: 0 1px 2px rgba(0,0,0,0.18);">{code}</span>
</div>

<p style="font-size: 13px; color: #9E8D7A; line-height: 1.8; margin-top: 16px;">
此验证码 <strong style="color: #C9A04A;">五分钟内有效</strong>，请尽快完成注册。<br/>
若非本人操作，请忽略此邮件。
</p>
</div>

<div style="text-align: center; padding-top: 16px; border-top: 1px solid #DED4C6;">
<p style="font-size: 11.5px; color: #C4B5A5; letter-spacing: 1px;">
此邮件由系统自动发出，请勿直接回复<br/>
© 墨香书阁 · 书香雅致
</p>
</div>
</div>"""

    msg = MIMEMultipart('alternative')
    msg['Subject'] = Header(subject, 'utf-8')
    # QQ SMTP 要求 From 头严格符合 RFC5322，中文显示名需编码
    msg['From'] = formataddr((str(Header('墨香书阁', 'utf-8')), config['sender_email']))
    msg['To'] = to_email

    html_part = MIMEText(body, 'html', 'utf-8')
    msg.attach(html_part)

    try:
        with smtplib.SMTP_SSL(config['smtp_host'], config['smtp_port'], timeout=10) as server:
            server.login(config['sender_email'], config['auth_code'])
            server.sendmail(config['sender_email'], [to_email], msg.as_string())
        return True
    except smtplib.SMTPAuthenticationError as e:
        raise ValueError('邮箱认证失败，请检查QQ邮箱授权码是否正确')
    except smtplib.SMTPRecipientsRefused as e:
        raise ValueError(f'收件邮箱被拒绝：{to_email}')
    except smtplib.SMTPServerDisconnected as e:
        raise ValueError('SMTP连接断开，请检查网络或SMTP服务器地址')
    except ConnectionRefusedError:
        raise ValueError('无法连接到SMTP服务器(smtp.qq.com:465)，请检查网络')
    except socket.timeout:
        raise ValueError('SMTP服务器连接超时，请稍后重试')
    except OSError as e:
        raise ValueError(f'网络异常：{str(e)}')
    except smtplib.SMTPException as e:
        raise ValueError(f'邮件发送失败：{str(e)}')
