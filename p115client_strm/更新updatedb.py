import subprocess
from alist import AlistClient
import json

def alist_print_storage_info_and_run_script(origin: str, username: str, password: str, user_id: str, db_folder: str, script_path: str):
    """
    获取符合条件的存储对象，并将 cookie 作为参数传递给 updatedb.py 脚本。
    
    参数：
    - origin: str，Alist 服务地址。
    - username: str，管理员用户名。
    - password: str，管理员密码。
    - user_id: str，用户 ID，用于在输出文件中命名。
    - db_folder: str，数据库文件夹路径，用于构建 db_file 路径。
    - script_path: str，updatedb.py 脚本的路径。
    """
    # 创建 Alist 客户端实例
    client = AlistClient(origin, username, password)
    
    # 获取存储列表
    storages = client.admin_storage_list()["data"]["content"]
    
    # 遍历存储对象，筛选符合条件的存储并执行脚本
    for storage in storages:
        # 检查存储的驱动类型是否是 '115 Cloud' 且 cookie 中包含指定的 UID
        if storage['driver'] == '115 Cloud':
            addition = json.loads(storage['addition'])
            cookie = addition.get('cookie', '')
            
            # 如果 cookie 包含用户 ID，执行 updatedb.py 脚本
            if f"UID={user_id}" in cookie:
                print(f"正在处理存储：{storage['mount_path']} (ID: {storage['id']})")
                print(f"存储对象完整内容:\n{storage}")
                
                # 构建 db_file 的路径，使用配置项 db_folder
                db_file = f'{db_folder}/115-{user_id}.db'
                command = [
                    'python', script_path,
                    '-c', cookie, '-f', db_file, '-cl' ,'/emby媒体库/'
                ]
                
                # 执行命令
                try:
                    subprocess.run(command, check=True)
                    print(f"成功执行脚本: {command}")
                except subprocess.CalledProcessError as e:
                    print(f"执行脚本失败: {e}")


def main():
    """
    主程序入口。
    """
    # Alist 服务信息  
    origin = "http://localhost:5244" 
    username = "test" 
    password = "test"
    
    # 配置项：115 用户 ID 和数据库文件夹路径
    user_id = "123456"  # 115 用户 ID 
    db_folder = r"/数据库/"  # 修改为你希望存储数据库文件的路径
    script_path = r"updatedb.py"  # 修改为你的 updatedb.py 脚本路径
    
    # 获取并处理 Alist 存储信息
    alist_print_storage_info_and_run_script(origin, username, password, user_id, db_folder, script_path)

if __name__ == "__main__":
    main()
