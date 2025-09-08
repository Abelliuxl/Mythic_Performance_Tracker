import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from config.settings import BROWSER_CONFIG
from utils.logger import logger

class BrowserManager:
    def __init__(self):
        self.config = BROWSER_CONFIG
    
    def create_driver(self):
        """创建浏览器驱动"""
        try:
            # 验证chromedriver路径
            chromedriver_path = self._get_chromedriver_path()
            if not chromedriver_path:
                raise FileNotFoundError("无法找到chromedriver.exe文件")
            
            logger.info(f"使用chromedriver路径: {chromedriver_path}")
            
            options = Options()
            
            # 应用配置
            if self.config.get("headless"):
                options.add_argument("--headless")
            if self.config.get("disable_gpu"):
                options.add_argument("--disable-gpu")
            if self.config.get("no_sandbox"):
                options.add_argument("--no-sandbox")
            if self.config.get("log_level"):
                options.add_argument(f"--log-level={self.config['log_level']}")
            if self.config.get("proxy_server"):
                options.add_argument(f"--proxy-server={self.config['proxy_server']}")
            if self.config.get("page_load_strategy"):
                options.page_load_strategy = self.config['page_load_strategy']
            
            # 创建服务
            service = Service(executable_path=chromedriver_path)
            
            # 创建驱动
            driver = webdriver.Chrome(service=service, options=options)
            logger.success("浏览器驱动创建成功")
            
            return driver
            
        except Exception as e:
            logger.error(f"创建浏览器驱动失败: {e}")
            raise
    
    def safe_quit(self, driver):
        """安全退出浏览器"""
        try:
            if driver:
                driver.quit()
                logger.info("浏览器已安全退出")
        except Exception as e:
            logger.warning(f"退出浏览器时出现错误: {e}")
    
    def stop_page_loading(self, driver):
        """停止页面加载"""
        try:
            driver.execute_script("window.stop();")
            logger.info("已停止页面资源加载")
        except Exception as e:
            logger.warning(f"无法停止页面加载: {e}")
    
    def wait_for_element(self, driver, by, value, timeout=10):
        """等待元素出现"""
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            logger.warning(f"等待元素超时: {value}")
            return None
    
    def wait_and_click(self, driver, by, value, timeout=10):
        """等待并点击元素"""
        element = self.wait_for_element(driver, by, value, timeout)
        if element:
            try:
                element.click()
                logger.info(f"成功点击元素: {value}")
                return True
            except Exception as e:
                logger.error(f"点击元素失败: {e}")
                return False
        return False
    
    def _get_chromedriver_path(self):
        """获取chromedriver路径，支持多种路径查找方式"""
        configured_path = self.config.get("chromedriver_path")
        
        if not configured_path:
            logger.error("未配置chromedriver路径")
            return None
        
        # 尝试直接使用配置的路径
        if os.path.exists(configured_path):
            return configured_path
        
        # 如果是相对路径，尝试在当前工作目录查找
        if not os.path.isabs(configured_path):
            current_dir_path = os.path.join(os.getcwd(), configured_path)
            if os.path.exists(current_dir_path):
                return current_dir_path
        
        # 尝试常见的chromedriver路径
        common_paths = [
            "chromedriver.exe",
            "chromedriver-win64/chromedriver.exe",
            "drivers/chromedriver.exe",
            "bin/chromedriver.exe",
            os.path.join(os.getcwd(), "chromedriver.exe"),
            os.path.join(os.getcwd(), "chromedriver-win64", "chromedriver.exe"),
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                logger.info(f"在常见路径中找到chromedriver: {path}")
                return path
        
        # 如果都没找到，记录错误
        logger.error(f"无法找到chromedriver.exe，已尝试路径: {configured_path}")
        logger.error(f"常见查找路径: {common_paths}")
        
        return None
