import requests
import argparse

# Emby服务器的地址和API密钥
EMBY_SERVER = 'http://localhost:8096'
API_KEY = ''

# 默认的媒体项目路径列表（可以包含多个文件或文件夹路径）
DEFAULT_MEDIA_PATHS = [
    r"/其他媒体路径3",
    r"/其他媒体路径1",
    r"/其他媒体路径2"
]

# 设置命令行参数解析
parser = argparse.ArgumentParser(description='触发Emby服务器的媒体库扫描')
parser.add_argument('--media-paths', type=str, nargs='*', default=DEFAULT_MEDIA_PATHS, help='要扫描的媒体项目的路径列表')
args = parser.parse_args()

# 获取媒体路径列表
MEDIA_PATHS = args.media_paths

# 构建API端点的URL
url = f'{EMBY_SERVER}/emby/Library/Refresh'

# 构建请求头
headers = {
    'X-MediaBrowser-Token': API_KEY,
    'Content-Type': 'application/json'
}

# 依次扫描每个媒体路径
for MEDIA_PATH in MEDIA_PATHS:
    data = {
        'Path': MEDIA_PATH,
        'Recursive': True,  # 如果需要递归扫描目录下的所有文件
        'RefreshLibrary': False  # 刷新整个库
    }
    
    try:
        # 发送POST请求
        response = requests.post(url, headers=headers, json=data)
        
        # 检查响应状态码
        if response.status_code == 204:
            print(f'成功触发了对 {MEDIA_PATH} 的库扫描')
        else:
            print(f'无法触发库扫描。状态码: {response.status_code}')
            print(response.text)
    except requests.RequestException as e:
        print(f'发生错误: {e}')
