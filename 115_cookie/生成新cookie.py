#!/usr/bin/env python3
# encoding: utf-8

import requests
from urllib.parse import urlencode

class AppEnum:
    web = 1
    ios = 6
    _115ios = 8
    android = 9
    _115android = 11
    _115ipad = 14
    tv = 15
    qandroid = 16
    windows = 19
    mac = 20
    linux = 21
    wechatmini = 22
    alipaymini = 23

def get_enum_name(val, cls):
    for key, value in cls.__dict__.items():
        if value == val or key == val:
            return key
    raise ValueError(f"Value {val} is not a valid {cls.__name__}")

def get_qrcode_token() -> dict:
    """获取登录二维码，扫码可用
    GET https://qrcodeapi.115.com/api/1.0/web/1.0/token/

    :return: 扫码相关的信息，比如二维码的 uid
    """
    api = "https://qrcodeapi.115.com/api/1.0/web/1.0/token/"
    return requests.get(api).json()

def post_qrcode_result(uid: str, app: str = "wechatmini") -> dict:
    """获取扫码登录的结果，并且绑定设备，包含 cookies
    POST https://passportapi.115.com/app/1.0/{app}/1.0/login/qrcode/

    :param uid: 二维码的 uid，取自 `login_qrcode_token` 接口响应
    :param app: 扫码绑定的设备，可以是 int、str 或者 AppEnum
    :return: 包含 cookies 的响应
    """
    app = get_enum_name(app, AppEnum)
    payload = {"app": app, "account": uid}
    api = f"https://passportapi.115.com/app/1.0/{app}/1.0/login/qrcode/"
    return requests.post(api, data=payload).json()

def login_with_autoscan(cookies: str, app: str = "wechatmini") -> dict:
    """自动扫码登录
    """
    headers = {"Cookie": cookies.strip()}
    token = get_qrcode_token()["data"]
    uid = token["uid"]
    # scanned
    scanned_data = requests.get(
        f"https://qrcodeapi.115.com/api/2.0/prompt.php?uid={uid}", 
        headers=headers
    ).json()["data"]
    # confirmed
    requests.post(
        scanned_data["do_url"], 
        data=scanned_data["do_params"], 
        headers=headers
    )
    return post_qrcode_result(uid, app)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="通过已有的 cookies 生成新的 cookies")
    parser.add_argument("-c", "--cookies", required=True, help="115 登录 cookies")
    parser.add_argument("-a", "--app", choices=("web", "ios", "115ios", "android", "115android", "115ipad", "tv", "qandroid", "windows", "mac", "linux", "wechatmini", "alipaymini"), default="wechatmini", help="选择一个 app 进行登录，默认为 'wechatmini'")
    args = parser.parse_args()

    try:
        new_cookies = login_with_autoscan(args.cookies, args.app)
        cookie_data = new_cookies["data"]["cookie"]
        formatted_cookies = f"UID={cookie_data['UID']}; CID={cookie_data['CID']}; SEID={cookie_data['SEID']; acw_tc={cookie_data['acw_tc']}"
        print("新的 cookies:", formatted_cookies)
    except Exception as e:
        print("生成新的 cookies 失败:", e)
