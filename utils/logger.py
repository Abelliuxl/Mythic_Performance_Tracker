import os
from datetime import datetime
from config.settings import FILE_PATHS

class Logger:
    def __init__(self, log_file=None):
        self.log_entries = []
        self.log_file = log_file or FILE_PATHS["log_file"]
        
        # 确保日志目录存在
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)
    
    def log(self, message):
        """记录日志信息"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        # 输出到控制台
        print(formatted_message)
        
        # 保存到内存
        self.log_entries.append(formatted_message)
    
    def error(self, message):
        """记录错误信息 / Log error message"""
        self.log(f"❌ 错误/ERROR: {message}")
    
    def warning(self, message):
        """记录警告信息 / Log warning message"""
        self.log(f"⚠ 警告/WARNING: {message}")
    
    def success(self, message):
        """记录成功信息 / Log success message"""
        self.log(f"✅ 成功/SUCCESS: {message}")
    
    def info(self, message):
        """记录一般信息 / Log info message"""
        self.log(f"ℹ 信息/INFO: {message}")
    
    def save_to_file(self):
        """将日志保存到文件 / Save log to file"""
        try:
            with open(self.log_file, "a", encoding="utf-8") as f: # Changed "w" to "a"
                for entry in self.log_entries:
                    f.write(entry + "\n")
            self.success(f"日志已保存到/Log saved to {self.log_file}")
        except Exception as e:
            self.error(f"保存日志文件失败/Failed to save log file: {e}")
    
    def get_log_entries(self):
        """获取所有日志条目 / Get all log entries"""
        return self.log_entries

# 全局日志实例
logger = Logger()

# 确保日志文件路径正确
def get_log_file_path():
    """获取日志文件路径"""
    from config.settings import FILE_PATHS
    return FILE_PATHS["log_file"]

# 重新初始化logger以确保路径正确
logger.log_file = get_log_file_path()
