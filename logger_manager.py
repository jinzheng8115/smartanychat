import logging
import os
from datetime import datetime

class LoggerManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(LoggerManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not LoggerManager._initialized:
            self.setup_logger()
            LoggerManager._initialized = True

    def setup_logger(self):
        """设置日志记录器"""
        # 创建logs目录（如果不存在）
        logs_dir = "logs"
        if not os.path.exists(logs_dir):
            os.makedirs(logs_dir)

        # 生成日志文件名（使用当前日期）
        current_date = datetime.now().strftime("%Y-%m-%d")
        log_file = os.path.join(logs_dir, f"chatanywhere_{current_date}.log")

        # 配置根日志记录器
        logger = logging.getLogger()
        logger.setLevel(logging.INFO)

        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)

        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # 创建格式化器
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # 设置格式化器
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # 添加处理器到日志记录器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        # 记录启动信息
        logging.info("=== ChatAnywhere 启动 ===")
        logging.info(f"日志文件: {log_file}")

    @staticmethod
    def get_logger():
        """获取日志记录器"""
        if LoggerManager._instance is None:
            LoggerManager()
        return logging.getLogger()
