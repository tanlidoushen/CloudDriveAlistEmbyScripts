from json import loads, dumps
from alist import AlistClient

def alist_update_pikpak_cloud_cookie(origin: str, username: str, password: str):
    """
    更新 Alist 中 `driver` 为 'PikPak' 的存储。
    
    参数：
    - origin: str，Alist 服务地址。
    - username: str，管理员用户名。
    - password: str，管理员密码。
    """
    # 创建 Alist 客户端实例
    client = AlistClient(origin, username, password)
    
    # 获取存储列表
    storages = client.admin_storage_list()["data"]["content"]
    
    # 筛选并更新 `driver` 为 'PikPak' 的存储
    for storage in storages:
        if storage["driver"] == "PikPak":
            # 使用 mount_path 替代 name
            print(f"正在处理存储：{storage['mount_path']} (ID: {storage['id']})")
            print(f"存储对象完整内容:\n{storage}")
            print("-" * 50)
            
            # 直接更新 `addition` 字段，保持原样
            addition = loads(storage["addition"])
            storage["addition"] = dumps(addition)
            
            # 提交更新
            client.admin_storage_update(storage)
            print(f"存储 {storage['mount_path']} 的信息更新成功！")

def main():
    """
    主程序入口。
    """
    # Alist 服务信息  
    origin = "http://localhost:5244" 
    username = "test" 
    password = "test"
    
    # 更新 Alist 存储
    alist_update_pikpak_cloud_cookie(origin, username, password)

if __name__ == "__main__":
    main()
