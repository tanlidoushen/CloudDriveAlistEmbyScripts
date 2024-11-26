import os
import concurrent.futures
import argparse
import shutil
from clouddrive import CloudDriveClient, CloudDriveFileSystem
from urllib.parse import quote  # 用于URL转码

# 默认配置
# 默认源目录
DEFAULT_SOURCE_DIRECTORY = "/网盘路径/emby媒体库"

# 默认目标目录
DEFAULT_TARGET_DIRECTORY = r"/本地路径\emby媒体库"

# 默认视频文件扩展名
DEFAULT_VIDEO_EXTENSIONS = ['.mkv', '.mp4', '.avi', '.rmvb']

# 是否复制元数据文件，默认为True
DEFAULT_COPY_METADATA = False

# 需要复制的元数据文件扩展名列表
DEFAULT_COPY_EXTENSIONS = ['.nfo', '.jpg', '.png']

# 需要替换的路径前缀
DEFAULT_REPLACE_PREFIX = "/网盘路径"

# 新的路径前缀
DEFAULT_NEW_PREFIX = "http://localhost:19798/static/http/localhost:19798/False/%2F网盘路径"

# 是否清理失效的.strm文件，默认为 True
DEFAULT_CLEANUP_STRM_FILES = True

# 是否清理失效的文件夹，默认为False
DEFAULT_CLEANUP_FOLDERS = False

# 是否清理失效的元数据文件，默认为False
DEFAULT_CLEANUP_METADATA = False

# 线程池的最大线程数
DEFAULT_NUM_THREADS = 8

# 是否启用哈希值功能，默认为 False
DEFAULT_USE_HASH = True

# 存储生成的.strm文件路径
generated_strm_files = set()

# 创建客户端对象，登录 CloudDrive
client = CloudDriveClient("http://localhost:19798", "test@test.com", "test")

fs = CloudDriveFileSystem(client)

def process_file(file_path, file_hash):
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension in video_extensions:
        relative_path = os.path.relpath(file_path, replace_prefix).replace("\\", "/")
        # 对relative_path进行URL转码
        encoded_relative_path = quote(relative_path, safe='')  # 转码所有字符，包括"/"

        # 使用转码后的路径构建新的URL
        if use_hash and file_hash:
            new_url = f"{new_prefix}%2F{encoded_relative_path}?sha1={file_hash}"
        else:
            new_url = f"{new_prefix}/{encoded_relative_path}"

        target_path = os.path.join(target_directory, os.path.relpath(os.path.dirname(file_path), source_directory))
        os.makedirs(target_path, exist_ok=True)
        strm_file_path = os.path.join(target_path, os.path.splitext(os.path.basename(file_path))[0] + '.strm')
        
        # 标准化路径
        strm_file_path = os.path.normpath(strm_file_path)
        
        if os.path.exists(strm_file_path):
            with open(strm_file_path, 'r', encoding='utf-8') as existing_strm:
                existing_url = existing_strm.read().strip()
            
            if existing_url == new_url:
                generated_strm_files.add(strm_file_path)
                return
        
        with open(strm_file_path, 'w', encoding='utf-8') as strm_file:
            strm_file.write(new_url)
            generated_strm_files.add(strm_file_path)
            print(f"生成.strm文件: {strm_file_path}")
    
    elif copy_metadata and file_extension in copy_extensions:
        target_path = os.path.join(target_directory, os.path.relpath(os.path.dirname(file_path), source_directory))
        os.makedirs(target_path, exist_ok=True)
        
        target_file_path = os.path.join(target_path, os.path.basename(file_path))
        
        if not os.path.exists(target_file_path):
            fs.download(file_path, target_file_path)
            print(f"复制文件: {file_path} -> {target_file_path}")

def cleanup_strm():
    print("开始清理失效的.strm文件...")
    for root, _, files in os.walk(target_directory):
        for file in files:
            if file.endswith('.strm'):
                strm_file_path = os.path.normpath(os.path.join(root, file))
                if strm_file_path not in generated_strm_files:
                    os.remove(strm_file_path)
                    print(f"删除失效的.strm文件: {strm_file_path}")

def cleanup_invalid_folders():
    print("开始清理失效的文件夹...")
    for root, dirs, _ in os.walk(target_directory, topdown=False):
        for dir in dirs:
            target_dir_path = os.path.normpath(os.path.join(root, dir))
            source_dir_path = target_dir_path.replace(target_directory, source_directory)
            if not fs.exists(source_dir_path):
                shutil.rmtree(target_dir_path)
                print(f"删除失效的文件夹: {target_dir_path}")

def cleanup_metadata():
    print("开始清理失效的元数据文件...")
    for root, _, files in os.walk(target_directory):
        for file in files:
            file_extension = os.path.splitext(file)[1].lower()
            if file_extension in copy_extensions:
                target_file_path = os.path.normpath(os.path.join(root, file))
                source_file_path = target_file_path.replace(target_directory, source_directory)
                if not fs.exists(source_file_path):
                    os.remove(target_file_path)
                    print(f"删除失效的元数据文件: {target_file_path}")

def main(source_directory, target_directory):
    print("开始处理文件...")
    for path, dirs, files in fs.walk_path(source_directory):
        for file in files:
            file_path = file.fullPathName
            file_hash = file.fileHashes.get('2') if file.fileHashes else None
            process_file(file_path, file_hash)
    
    if cleanup_strm_files:
        cleanup_strm()
    
    if enable_cleanup_folders:
        cleanup_invalid_folders()
    
    if enable_cleanup_metadata:
        cleanup_metadata()

    print("处理完成。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="处理媒体文件并管理 .strm 文件。")
    parser.add_argument('--source', '-s', type=str, help='媒体文件的源目录')
    parser.add_argument('--target', '-t', type=str, help='处理后文件和 .strm 文件的目标目录')
    parser.add_argument('--cleanup-folders', '-cf', action='store_true', help='启用失效文件夹清理')
    parser.add_argument('--cleanup-metadata', '-cm', action='store_true', help='启用失效元数据清理')
    parser.add_argument('--use-hash', '-uh', action='store_true', help='启用哈希值功能')

    args = parser.parse_args()

    # 根据命令行参数或默认配置设置目录
    source_directory = args.source if args.source else DEFAULT_SOURCE_DIRECTORY  # 源目录
    target_directory = args.target if args.target else DEFAULT_TARGET_DIRECTORY  # 目标目录
    enable_cleanup_folders = args.cleanup_folders if args.cleanup_folders else DEFAULT_CLEANUP_FOLDERS  # 是否清理失效文件夹
    enable_cleanup_metadata = args.cleanup_metadata if args.cleanup_metadata else DEFAULT_CLEANUP_METADATA  # 是否清理失效元数据
    use_hash = args.use_hash if args.use_hash else DEFAULT_USE_HASH  # 是否启用哈希值功能

    # 使用默认配置的其他参数
    video_extensions = DEFAULT_VIDEO_EXTENSIONS  # 视频文件扩展名列表
    copy_metadata = DEFAULT_COPY_METADATA  # 是否复制元数据文件
    copy_extensions = DEFAULT_COPY_EXTENSIONS  # 需要复制的元数据文件扩展名列表
    replace_prefix = DEFAULT_REPLACE_PREFIX  # 需要替换的路径前缀
    new_prefix = DEFAULT_NEW_PREFIX  # 新的路径前缀
    cleanup_strm_files = DEFAULT_CLEANUP_STRM_FILES  # 是否清理失效的 .strm 文件
    num_threads = DEFAULT_NUM_THREADS  # 线程池的最大线程数

    # 运行主函数
    main(source_directory, target_directory)
