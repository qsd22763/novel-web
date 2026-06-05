import os
import json
import requests

QQ_APP_ID = os.environ.get('QQ_APP_ID', '')
QQ_APP_SECRET = os.environ.get('QQ_APP_SECRET', '')
WECHAT_APP_ID = os.environ.get('WECHAT_APP_ID', '')
WECHAT_APP_SECRET = os.environ.get('WECHAT_APP_SECRET', '')
OAUTH_REDIRECT_URI = os.environ.get('OAUTH_REDIRECT_URI', 'http://localhost:5173/login')
OAUTH_CALLBACK_URL = os.environ.get('OAUTH_CALLBACK_URL', 'http://localhost:8000/api/auth/oauth_callback/')


# ==================== QQ OAuth ====================

def get_qq_auth_url(redirect_uri=None, state=''):
    """构造QQ授权URL"""
    if redirect_uri is None:
        redirect_uri = OAUTH_REDIRECT_URI
    return (
        f'https://graph.qq.com/oauth2.0/authorize'
        f'?response_type=code&client_id={QQ_APP_ID}'
        f'&redirect_uri={redirect_uri}&state={state}'
    )


def get_qq_access_token(code):
    """用授权码换取access_token（redirect_uri必须与授权步骤一致）"""
    url = (
        f'https://graph.qq.com/oauth2.0/token'
        f'?grant_type=authorization_code&client_id={QQ_APP_ID}'
        f'&client_secret={QQ_APP_SECRET}&code={code}&redirect_uri={OAUTH_REDIRECT_URI}'
    )
    try:
        resp = requests.post(url, timeout=10)
        resp.raise_for_status()
        text = resp.text
        if text.startswith('{'):
            return json.loads(text)
        result = {}
        for item in text.split('&'):
            key, value = item.split('=', 1)
            result[key] = value
        return result
    except requests.RequestException as e:
        raise Exception(f'QQ获取access_token失败: {str(e)}')


def get_qq_openid(access_token):
    """获取openid和unionid"""
    url = f'https://graph.qq.com/oauth2.0/me?access_token={access_token}'
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        text = resp.text
        start = text.index('(') + 1
        end = text.rindex(')')
        data = json.loads(text[start:end])
        return data.get('openid', ''), data.get('unionid', '')
    except (requests.RequestException, ValueError, IndexError) as e:
        raise Exception(f'QQ获取openid失败: {str(e)}')


def get_qq_userinfo(access_token, openid):
    """获取QQ用户昵称头像"""
    url = (
        f'https://graph.qq.com/user/get_user_info'
        f'?access_token={access_token}&oauth_consumer_key={QQ_APP_ID}&openid={openid}'
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise Exception(f'QQ获取用户信息失败: {str(e)}')


# ==================== 微信OAuth ====================

def get_wechat_auth_url(redirect_uri=None, state=''):
    """构造微信扫码授权URL"""
    if redirect_uri is None:
        redirect_uri = OAUTH_REDIRECT_URI
    return (
        f'https://open.weixin.qq.com/connect/qrconnect'
        f'?appid={WECHAT_APP_ID}&redirect_uri={redirect_uri}'
        f'&response_type=code&scope=snsapi_login&state={state}#wechat_redirect'
    )


def get_wechat_access_token(code):
    """用授权码换取微信access_token"""
    url = (
        f'https://api.weixin.qq.com/sns/oauth2/access_token'
        f'?appid={WECHAT_APP_ID}&secret={WECHAT_APP_SECRET}'
        f'&code={code}&grant_type=authorization_code'
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise Exception(f'微信获取access_token失败: {str(e)}')


def get_wechat_userinfo(access_token, openid):
    """获取微信用户信息"""
    url = (
        f'https://api.weixin.qq.com/sns/userinfo'
        f'?access_token={access_token}&openid={openid}&lang=zh_CN'
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        raise Exception(f'微信获取用户信息失败: {str(e)}')
