import sqlite3
import os
import urllib.parse
import hashlib

# 配置字典：集中管理所有可配置项
config = {
    'db_path': r'115-123456.db',  # SQLite 数据库文件路径
    'target_dir': r'\strm存放目录\',   # 目标目录路径，创建目录结构和 .strm 文件
    'video_extensions': ['.mp4', '.mkv', '.avi'],  # 视频文件的后缀名列表
    'emby_media_path': '/emby媒体库/',  # 需要匹配的路径部分
    'url_prefix': 'http://localhost:19798/static/http/localhost:19798/False/%2F115'  # URL 前缀
}

# 打开 SQLite 数据库
conn = sqlite3.connect(config['db_path'])
cursor = conn.cursor()

# 构建 SQL 查询条件
video_ext_condition = ' OR '.join([f"path LIKE '%{ext}'" for ext in config['video_extensions']])
sql_query = f"""
SELECT name, path, sha1
FROM data
WHERE ({video_ext_condition})
AND path LIKE '%{config['emby_media_path']}%'
"""

# 执行查询
cursor.execute(sql_query)

# 检查 .strm 文件内容是否正确
def check_strm_file(strm_file_path, expected_url):
    if os.path.exists(strm_file_path):
        with open(strm_file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            return content == expected_url
    return False

# 遍历符合条件的记录
for row in cursor.fetchall():
    name, path, sha1 = row
    
    # 获取文件名不包含后缀
    file_name = os.path.splitext(name)[0]
    
    # 构建目标目录路径（直接根据 path 字段）
    full_path = os.path.join(config['target_dir'], path.split(config['emby_media_path'], 1)[-1])
    
    # 获取目录部分，不包括文件名
    directory_path = os.path.dirname(full_path)
    
    # URL 转码，safe='' 表示不允许任何字符保持原样
    encoded_path = urllib.parse.quote(path, safe='')

    # 拼接 URL 前缀和 SHA1 校验码
    expected_url = f"{config['url_prefix']}{encoded_path}?sha1={sha1}"
    
    # 检查目录是否存在，如果不存在则创建
    if not os.path.exists(directory_path):
        os.makedirs(directory_path, exist_ok=True)
    
    # 检查 .strm 文件是否存在并验证其内容
    strm_file_path = os.path.join(directory_path, file_name + '.strm')
    
    if check_strm_file(strm_file_path, expected_url):
        print(f"跳过：{strm_file_path}（文件已存在且内容正确）")
    else:
        # 如果文件内容不正确或文件不存在，则写入正确的内容
        with open(strm_file_path, 'w', encoding='utf-8') as f:
            f.write(expected_url)  # 将拼接后的 URL 写入 .strm 文件
        
        print(f"已创建或更新：{strm_file_path}，内容：{expected_url}")

# 关闭数据库连接
conn.close()
