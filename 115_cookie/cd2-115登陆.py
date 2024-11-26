import grpc
import argparse
from clouddrive.proto import CloudDrive_pb2
from clouddrive import CloudDriveClient

def login_with_editthiscookie(client, cookie_value):
    request = CloudDrive_pb2.Login115EditthiscookieRequest(editThiscookieString=cookie_value)
    
    try:
        result = client.APILogin115Editthiscookie(request)
        
        # 根据返回的结果判断并打印
        if result.success:
            print(f"登陆成功，结果：{result}")
        else:
            print(f"登陆失败，结果：{result}")
        return result
    except grpc.RpcError as e:
        print(f"RPC 错误，结果：{e}")
        return None

def main():
    # 使用 argparse 解析命令行参数
    parser = argparse.ArgumentParser(description="使用 Cookie 登录 115")
    parser.add_argument('-c', '--cookie', required=True, help="115 的 cookie 字符串")
    args = parser.parse_args()
    
    cookie_value = args.cookie
    
    # 创建 CloudDriveClient 实例，连接到本地 CloudDrive 服务   
    client = CloudDriveClient("http://localhost:19798", "test@test.com", "test")
    
    # 调用登录函数
    login_with_editthiscookie(client, cookie_value)

# 运行主函数
if __name__ == "__main__":
    main()
