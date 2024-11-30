import subprocess
import random
import time
import json
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

# 随机生成延迟时间，单位为秒
delay = random.randint(0, 0)  # 设置延迟时间为0秒
print(f"将在{delay // 60}分钟后执行签到任务...")

# 等待随机延迟时间
time.sleep(delay)

# Alist 服务信息
origin = "http://localhost:5244"
username = "test"
password = "test"

# 获取 '115 Cloud' 存储的 cookies
authentication_cookies = get_115_cloud_cookies(origin, username, password)

# 循环处理每个账号的签到
for idx, cookie in enumerate(authentication_cookies, start=1):
    # 构建命令
    command = f'p115 check -c "{cookie}"'

    # 调用命令并获取输出
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # 解析输出
    output = result.stdout.strip()
    if result.returncode == 0:
        print(f"账号{idx}签到成功！")
        print("返回信息：")
        print(output)
    else:
        print(f"账号{idx}签到失败。错误信息：")
        print(result.stderr)
    print()  # 打印空行，用于分隔不同账号的输出
