import subprocess
from json import loads, dumps
from alist import AlistClient

def extract_cookie_from_storage(storage: dict) -> str:
    """
    从存储对象中提取旧的 cookie。
    
    参数：
    - storage: dict，存储对象。
    
    返回：
    - str，提取的旧 cookie。
    """
    addition = loads(storage["addition"])
    return addition.get("cookie", "")

def generate_new_cookie(script_path: str, old_cookie: str) -> str:
    """
    调用外部脚本生成新的 cookie。
    
    参数：
    - script_path: str，生成新 cookie 的脚本路径。
    - old_cookie: str，旧的 cookie，作为外部脚本的输入参数。
    
    返回：
    - str，新的 cookie。
    """
    try:
        # 使用 subprocess 调用脚本，传入旧的 cookie
        result = subprocess.run(
            ["python", script_path, "-c", old_cookie],
            capture_output=True,
            text=True,
            check=True,
        )
        # 从脚本输出中提取新的 cookie
        for line in result.stdout.splitlines():
            if line.startswith("新的 cookies:"):
                return line.split("新的 cookies:", 1)[1].strip()
    except subprocess.CalledProcessError as e:
        print(f"执行脚本出错：{e.stderr}")
        raise RuntimeError("无法生成新的 cookie")
    raise ValueError("未从脚本输出中找到新的 cookie")

def login_to_clouddrive_with_new_cookie(cookie: str, script_path: str):
    """
    使用新生成的 cookie 登录 CloudDrive中的115。
    
    参数：
    - cookie: str，新生成的 cookie。
    - script_path: str，登录脚本路径。
    """
    # 调用 cd2-115登陆.py 脚本进行登录
    result = subprocess.run(
        ["python", script_path, "-c", cookie],
        capture_output=True,
        text=True,
        check=True,
    )
    # 输出登录结果
    print(f"{result.stdout.strip()}")


def alist_update_115_cloud_cookie(origin: str, username: str, password: str, script_path: str, login_script_path: str):
    """
    更新 Alist 中 `driver` 为 '115 Cloud' 的存储的 cookie，并登录 115 Cloud。
    
    参数：
    - origin: str，Alist 服务地址。
    - username: str，管理员用户名。
    - password: str，管理员密码。
    - script_path: str，生成新 cookie 的脚本路径。
    - login_script_path: str，登录脚本路径。
    """
    # 创建 Alist 客户端实例
    client = AlistClient(origin, username, password)
    
    # 获取存储列表
    storages = client.admin_storage_list()["data"]["content"]
    
    # 筛选并更新 `driver` 为 '115 Cloud' 的存储
    for storage in storages:
        if storage["driver"] == "115 Cloud":
            # 使用 mount_path 替代 name
            print(f"正在处理存储：{storage['mount_path']} (ID: {storage['id']})")
            print(f"存储对象完整内容:\n{storage}")
            print("-" * 50)
            
            # 提取旧的 cookie
            old_cookie = extract_cookie_from_storage(storage)
            print(f"提取的旧 cookie: {old_cookie}")
            
            # 生成新的 cookie
            print("正在生成新的 cookie...")
            new_cookie = generate_new_cookie(script_path, old_cookie)
            print(f"新的 cookie: {new_cookie}")
            
            # 更新 addition 中的 cookie
            addition = loads(storage["addition"])
            addition["cookie"] = new_cookie
            storage["addition"] = dumps(addition)
            
            # 提交更新
            client.admin_storage_update(storage)
            print(f"存储 {storage['mount_path']} 的 cookie 更新成功！")
            
            # 登录 CloudDrive中的115
            print("正在登录 CloudDrive 中的 115 ...")
            login_to_clouddrive_with_new_cookie(new_cookie, login_script_path)

def main():
    """
    主程序入口。
    """
    # Alist 服务信息 
    origin = "http://localhost:5244" 
    username = "test" 
    password = "test"
    
    # 脚本路径
    script_path = r"生成新cookie.py"
    login_script_path = r"cd2-115登陆.py"
    
    # 更新 Alist 存储并登录
    alist_update_115_cloud_cookie(origin, username, password, script_path, login_script_path)

if __name__ == "__main__":
    main()
