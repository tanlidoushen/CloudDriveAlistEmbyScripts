#!/usr/bin/env python3
# encoding: utf-8

import time
import json
from p115 import P115Client
from p115.tool import crack_captcha
from alist import AlistClient


# 从 Alist 获取 115 Cloud 存储的 cookie
def get_115_cloud_cookies(origin: str, username: str, password: str):
    """
    从 Alist 中获取所有 '115 Cloud' 存储的 cookie 信息。

    参数：
    - origin: str，Alist 服务地址。
    - username: str，管理员用户名。
    - password: str，管理员密码。

    返回：
    - cookies: list，包含多个账号 cookie 的列表。
    """
    # 创建 Alist 客户端实例
    client = AlistClient(origin, username, password)
    
    # 获取存储列表
    storages = client.admin_storage_list()["data"]["content"]
    
    # 提取所有 '115 Cloud' 存储的 cookie
    cookies = []
    for storage in storages:
        if storage["driver"] == "115 Cloud":
            # 解析出 cookie
            storage_addition = json.loads(storage["addition"])
            cookie = storage_addition.get("cookie")
            if cookie:
                cookies.append(cookie)
    
    # 打印获取到的 cookie 数量
    print(f"已从 Alist 中获取到 {len(cookies)} 个 115 Cloud 存储的 cookie。")
    
    return cookies


class P115AutoCrack:
    def __init__(self, cookie):
        self.client = P115Client(cookie)
        self.pickcode = 'x'

    def auto_crack(self):
        print("开始识别验证码...")
        while not crack_captcha(self.client):
            print("验证码识别失败，正在重试...")

    def check_account(self):
        """
        对每个账号执行风控检测，如果检测到风控，则尝试破解验证码。
        """
        crack_flag = False
        result = self.client.download_url_web(self.pickcode)
        
        # 检测是否风控（code == 911）
        if not result.get('state', True) and result.get('code', 9999) == 911:
            crack_flag = True
            print("检测到风控，尝试破解验证码...")
            self.auto_crack()
            time.sleep(3)
            result = self.client.download_url_web(self.pickcode)
        
        # 检测风控解除（msg_code == 70005 或 msg_code == 0）
        if (not result.get('state', True) and result.get('msg_code', 9999) == 70005) or (result.get('state', False) and result.get('msg_code', 9999) == 0):
            if crack_flag:
                print("解除风控成功")
            else:
                print("未检测到风控")
        else:
            print("账号异常，无法解除风控。")


def main():
    # Alist 服务信息
    origin = "http://localhost:5244"  # Alist 服务地址
    username = "test"  # Alist 管理员用户名
    password = "test"  # Alist 管理员密码
    
    # 获取 '115 Cloud' 存储的 cookies
    authentication_cookies = get_115_cloud_cookies(origin, username, password)
    
    # 对每个 cookie 进行风控检测
    for cookie in authentication_cookies:
        print(f"开始检测 cookie：{cookie}")
        auto_crack = P115AutoCrack(cookie)
        auto_crack.check_account()
        time.sleep(2)  # 每个 cookie 检测完成后等待 2 秒


if __name__ == "__main__":
    main()
