import time
import os
import pickle
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from config.settings import BROWSER_CONFIG, SESSION_CONFIG
from utils.logger import logger
from utils.platform_utils import platform_utils


class BrowserManager:
    def __init__(self):
        self.config = BROWSER_CONFIG
        self.session_config = SESSION_CONFIG

    def _get_user_data_dir(self):
        project_root = os.getcwd()
        data_dir_name = self.session_config.get("user_data_dir", "chrome_profile")
        data_dir = os.path.join(project_root, data_dir_name)
        os.makedirs(data_dir, exist_ok=True)
        return data_dir

    def create_driver(self, use_persistent_session=True):
        try:
            chromedriver_path = self._get_chromedriver_path()
            if not chromedriver_path:
                raise FileNotFoundError("无法找到chromedriver文件")

            options = Options()

            if self.config.get("headless"):
                options.add_argument("--headless=new")
            if self.config.get("disable_gpu"):
                options.add_argument("--disable-gpu")
            if self.config.get("no_sandbox"):
                options.add_argument("--no-sandbox")
            if self.config.get("disable_dev_shm_usage"):
                options.add_argument("--disable-dev-shm-usage")
            if self.config.get("disable_setuid_sandbox"):
                options.add_argument("--disable-setuid-sandbox")
            if self.config.get("log_level"):
                options.add_argument(f"--log-level={self.config['log_level']}")
            if self.config.get("proxy_server"):
                options.add_argument(f"--proxy-server={self.config['proxy_server']}")
            if self.config.get("page_load_strategy"):
                options.page_load_strategy = self.config["page_load_strategy"]
            if self.config.get("window_size"):
                options.add_argument(f"--window-size={self.config['window_size']}")
            if self.config.get("user_agent"):
                options.add_argument(f"user-agent={self.config['user_agent']}")

            options.add_argument("--remote-debugging-port=9222")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)

            if use_persistent_session:
                user_data_dir = self._get_user_data_dir()
                options.add_argument(f"--user-data-dir={user_data_dir}")
                logger.info(f"使用持久化用户数据目录: {user_data_dir}")

            platform_config = platform_utils.get_platform_config()
            browser_options = platform_config.get("browser_options", {})

            if browser_options.get("headless_arg"):
                options.add_argument(browser_options["headless_arg"])
            if browser_options.get("gpu_arg"):
                options.add_argument(browser_options["gpu_arg"])
            if browser_options.get("sandbox_arg"):
                options.add_argument(browser_options["sandbox_arg"])
            if browser_options.get("xvfb_arg"):
                options.add_argument(browser_options["xvfb_arg"])

            chrome_binary = platform_utils.get_chrome_binary_path()
            if chrome_binary:
                options.binary_location = chrome_binary

            service = Service(executable_path=chromedriver_path)

            driver = webdriver.Chrome(service=service, options=options)

            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                Object.defineProperty(navigator, 'webdriver', { get: () => undefined });
                Object.defineProperty(navigator, 'plugins', { get: () => [1,2,3,4,5] });
                Object.defineProperty(navigator, 'languages', { get: () => ['zh-CN', 'zh', 'en'] });
                """
            })

            logger.success("浏览器驱动创建成功")
            return driver

        except Exception as e:
            logger.error(f"创建浏览器驱动失败: {e}")
            raise

    def safe_quit(self, driver):
        try:
            if driver:
                driver.quit()
                logger.info("浏览器已安全退出")
        except Exception as e:
            logger.warning(f"退出浏览器时出现错误: {e}")

    def stop_page_loading(self, driver):
        try:
            driver.execute_script("window.stop();")
        except Exception as e:
            logger.warning(f"无法停止页面加载: {e}")

    def wait_for_element(self, driver, by, value, timeout=10):
        try:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((by, value))
            )
            return element
        except Exception as e:
            logger.warning(f"等待元素超时: {value}")
            return None

    def wait_and_click(self, driver, by, value, timeout=10):
        element = self.wait_for_element(driver, by, value, timeout)
        if element:
            try:
                element.click()
                return True
            except Exception as e:
                logger.error(f"点击元素失败: {e}")
                return False
        return False

    def _get_chromedriver_path(self):
        platform_path = platform_utils.get_chromedriver_path()
        if platform_path:
            return platform_path

        configured_path = self.config.get("chromedriver_path")
        if configured_path and os.path.exists(configured_path):
            return configured_path

        if configured_path and not os.path.isabs(configured_path):
            current_dir_path = os.path.join(os.getcwd(), configured_path)
            if os.path.exists(current_dir_path):
                return current_dir_path

        platform_config = platform_utils.get_platform_config()
        platform_name = platform_config["platform"]

        platform_specific_paths = {
            "windows": [
                "chromedriver.exe",
                "chromedriver-win64/chromedriver.exe",
                "drivers/chromedriver.exe",
                os.path.join(os.getcwd(), "chromedriver.exe"),
                os.path.join(os.getcwd(), "chromedriver-win64", "chromedriver.exe"),
            ],
            "linux": [
                "chromedriver",
                "chromedriver-linux64/chromedriver",
                "drivers/chromedriver",
                os.path.join(os.getcwd(), "chromedriver"),
                os.path.join(os.getcwd(), "chromedriver-linux64", "chromedriver"),
            ],
            "macos": [
                "chromedriver",
                "chromedriver-mac-x64/chromedriver",
                "drivers/chromedriver",
                os.path.join(os.getcwd(), "chromedriver"),
                os.path.join(os.getcwd(), "chromedriver-mac-x64", "chromedriver"),
            ]
        }

        paths = platform_specific_paths.get(platform_name, platform_specific_paths["linux"])
        for path in paths:
            if os.path.exists(path):
                logger.info(f"找到chromedriver: {path}")
                return path

        logger.error(f"无法找到chromedriver")
        return None

    def is_logged_in(self, driver):
        try:
            driver.get("https://wow.blizzard.cn/character/")
            time.sleep(3)
            if "login" in driver.current_url.lower():
                return False
            return True
        except Exception as e:
            logger.warning(f"检查登录状态失败: {e}")
            return False
