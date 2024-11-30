import time
import errno
from p115 import P115Client, P115FileSystem
from p115.tool import wish_make, wish_answer, wish_adopt
import subprocess
from alist import AlistClient
import json

# 从 Alist 获取存储信息并返回 115 Cloud 存储的 cookie
def get_cookies_from_alist(origin: str, username: str, password: str, user_id: str):
    """
    获取 Alist 中的 115 Cloud 存储信息并返回用户对应的 cookie。
    
    参数：
    - origin: Alist 服务地址
    - username: Alist 管理员用户名
    - password: Alist 管理员密码
    - user_id: 需要获取 cookie 的用户 ID
    
    返回：
    - 返回祝愿账号的 cookie 和许愿账号的 cookies
    """
    client = AlistClient(origin, username, password)
    storages = client.admin_storage_list()["data"]["content"]

    # 用于存储 cookies 的列表
    wish_cookies = []
    wish_cookie = None  # 用于保存祝愿账号的 cookie

    for storage in storages:
        if storage['driver'] == '115 Cloud':
            addition = json.loads(storage['addition'])
            cookie = addition.get('cookie', '')
            
            # 如果 cookie 包含用户 ID，则认为这是祝愿账号
            if f"UID={user_id}" in cookie:
                wish_cookie = cookie  # 找到祝愿账号的 cookie
            else:
                wish_cookies.append(cookie)  # 添加许愿账号的 cookie

    print(f"已从 Alist 中获取到 {len(wish_cookies) + 1} 个 115 Cloud 存储的 cookie，许愿账号 {len(wish_cookies)} 个，祝愿账号 1 个。")
    
    return wish_cookie, wish_cookies


def main():
    # Alist 服务信息
    origin =  "http://localhost:5244"
    username = "test"
    password = "test"
    user_id = "123456"  # 祝愿账号的用户 ID

    # 获取 cookies
    wish_cookie, wish_cookies = get_cookies_from_alist(origin, username, password, user_id)

    if not wish_cookie:
        print(f"未找到祝愿账号 (UID={user_id}) 的 cookie。")
        return

    # 许愿账号的 cookie 列表
    accounts = [{'cookies': cookie, 'content': '希望下载速度更快', 'size': 5} for cookie in wish_cookies]

    # 遍历每个账号并创建许愿
    for idx, account in enumerate(accounts, start=1):
        # 初始化 115 客户端
        client = P115Client(cookies=account['cookies'])
        
        try:
            # 创建许愿
            wish_id = wish_make(client, account['content'], account['size'])
            print(f'账号{idx}，许愿已创建，许愿 ID: {wish_id}')
            
            # 使用祝愿账号的 cookie 进行助愿操作
            try:
                # 在每次请求之前添加 10 秒的延迟
                time.sleep(10)
                
                # 创建助愿
                aid_id = wish_answer(P115Client(cookies=wish_cookie), wish_id, '帮你助个愿')
                print(f'许愿 ID {wish_id}，助愿已创建，助愿 ID: {aid_id}')
                
                # 等待一段时间，避免请求频繁
                time.sleep(10)
                
                # 执行采纳助愿
                response = wish_adopt(client, wish_id, aid_id)
                print(f'账号{idx}，采纳助愿 {aid_id} 成功。')
                
            except OSError as e:
                if e.args[0] == errno.EIO and e.args[1]['code'] == 40201020:
                    print(f'许愿 ID {wish_id}，已提交过助愿，跳过。')
                else:
                    raise e  # 如果不是已提交助愿的错误，则重新抛出异常
        
        except OSError as e:
            if e.args[0] == errno.EIO and e.args[1]['code'] == 40201045:
                print(f'账号{idx}，发布心愿次数不足，跳过。')
            else:
                raise e  # 如果不是发布心愿次数不足的错误，则重新抛出异常


if __name__ == '__main__':
    main()
