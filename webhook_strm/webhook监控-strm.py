from flask import Flask, request, jsonify
import os
import subprocess
import logging
import time
from threading import Timer

app = Flask(__name__)

# 设置 Flask 日志级别为 ERROR，减少输出
app.logger.setLevel(logging.ERROR)

# 禁用 Werkzeug 的日志
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

class FileNotifyHandler:
    def __init__(self):
        self.wait_time = 10  # 等待时间（秒）
        self.all_directories = []  # 用于存储路径信息列表
        self.last_event_time = 0  # 上一次事件的时间戳
        self.timer = None  # 定时器

        # 配置可处理的文件后缀和关键词
        self.allowed_extensions = {".mkv", ".mp4", ".avi"}
        self.allowed_keywords = {"/emby媒体库"}

    def reset_timer(self):
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(self.wait_time, self.process_changes)
        self.timer.start()

    def add_change(self, path):
        # 过滤文件后缀
        if not self._is_valid_file(path):
            return

        # 提取目录部分
        dir_path = os.path.dirname(path)

        # 记录路径（避免重复）
        if dir_path not in self.all_directories:
            self.all_directories.append(dir_path)
        self.last_event_time = time.time()
        self.reset_timer()

    def process_changes(self):
        # 等待时间后执行处理逻辑
        if not self.all_directories:
            return

        print("开始处理文件变动...")
        param_list = self.all_directories

        # 执行脚本1和脚本2
        execute_scripts(param_list)

        # 清空记录
        self.all_directories.clear()

    def _is_valid_file(self, path):
        """
        判断路径是否满足后缀和关键词要求
        """
        if not any(keyword in path for keyword in self.allowed_keywords):
            return False
        _, ext = os.path.splitext(path)
        return ext.lower() in self.allowed_extensions

handler = FileNotifyHandler()

def translate_action(action, source_file, destination_file):
    """
    翻译文件操作类型，并区分“移动”和“重命名”
    """
    if action == "rename":
        source_dir = os.path.dirname(source_file)
        dest_dir = os.path.dirname(destination_file)
        if source_dir != dest_dir:
            return "移动"
        else:
            return "重命名"
    translations = {
        "create": "创建",
        "delete": "删除"
    }
    return translations.get(action, "未知操作")

def execute_scripts(param_list):
    """
    执行脚本1和脚本2
    """
    # 替换关键词前和替换后
    param_source_list = param_list
    param_target_list = [
        path.replace('/网盘路径', r'/本地路径').replace('/', '\\')
        for path in param_list
    ]

    # 执行脚本1
    for source, target in zip(param_source_list, param_target_list):
        script1_cmd = [
            'python', r'sha1-strm-完整路径-url转码.py',
            '--source', source,
            '--target', target
        ]
        print(f"正在执行脚本1: {' '.join(script1_cmd)}")
        subprocess.run(script1_cmd, shell=True)

    # 执行脚本2
    script2_cmd = [
        'python', r'emby扫库.py',
        '--media-paths'
    ] + param_target_list
    print(f"正在执行脚本2: {' '.join(script2_cmd)}")
    subprocess.run(script2_cmd, shell=True)

@app.route('/file_notify', methods=['POST'])
def file_notify():
    """
    接收文件系统监听器的 webhook POST 请求
    """
    data = request.json
    if not data:
        return jsonify({"状态": "错误", "消息": "无效的 JSON 数据"}), 400

    notifications = []

    for item in data.get("data", []):
        source_file = item.get("source_file", "未知路径")
        destination_file = item.get("destination_file", "无")
        action_cn = translate_action(item.get("action", "未知"), source_file, destination_file)
        is_dir_cn = "目录" if item.get("is_dir") == "true" else "文件"

        notification = {
            "动作": action_cn,
            "类型": is_dir_cn,
            "源路径": source_file,
            "目标路径": destination_file
        }
        notifications.append(notification)

        # 根据操作记录目录变动
        if action_cn in ["移动", "重命名", "创建", "删除"]:
            handler.add_change(source_file)
            handler.add_change(destination_file)

    # 打印通知信息
    print(f"收到文件变更通知： {notifications}")

    # 响应
    return jsonify({"状态": "成功", "消息": "已接收文件系统通知"}), 200

if __name__ == '__main__':
    # 启动 Flask 应用，监听 9991 端口
    app.run(host='0.0.0.0', port=9991, debug=True, use_reloader=False)
