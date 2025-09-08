import time
import sys
import os
import pandas as pd
from urllib.parse import quote
from selenium.webdriver.common.by import By

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import FILE_PATHS, BROWSER_CONFIG, WCL_BASE_URL, WCL_ZONE_ID
from utils.logger import logger
from utils.browser_manager import BrowserManager

def build_wcl_url(server, character_name):
    """构建WCL URL"""
    return f"{WCL_BASE_URL}/character/cn/{quote(server.strip(), safe='')}/{quote(character_name.strip(), safe='')}?zone={WCL_ZONE_ID}"

def click_update_with_retry(driver, url, max_attempts=3):
    """重试机制点击Update按钮"""
    for attempt in range(1, max_attempts + 1):
        try:
            driver.get(url)
            time.sleep(6)
            update_button = driver.find_element(By.ID, "update-link")
            update_button.click()
            logger.success(f"成功点击 Update（第 {attempt} 次）：{url}")
            time.sleep(2)
            return True
        except Exception as e:
            logger.warning(f"第 {attempt} 次尝试失败：{e}")
            time.sleep(2)
    
    logger.error(f"多次点击失败，跳过：{url}")
    return False

def main():
    """主函数"""
    logger.info("=== 开始执行WCL更新点击器 ===")
    
    # 读取角色列表
    try:
        char_df = pd.read_excel(FILE_PATHS["character_info"])
        logger.success(f"成功读取角色文件: {FILE_PATHS['character_info']}")
    except Exception as e:
        logger.error(f"无法读取角色文件：{e}")
        return False
    
    # 创建浏览器管理器
    browser_manager = BrowserManager()
    driver = None
    
    try:
        # 创建浏览器驱动
        driver = browser_manager.create_driver()
        
        # 遍历角色并点击 Update
        for _, row in char_df.iterrows():
            name = str(row["角色名"]).strip()
            server = str(row["服务器"]).strip()
            url = build_wcl_url(server, name)
            
            logger.info(f"\n🔍 正在处理角色：{name}（{server}）")
            click_update_with_retry(driver, url)
        
        logger.success("=== WCL更新点击器执行完成 ===")
        return True
        
    except Exception as e:
        logger.error(f"程序执行出现错误：{e}")
        return False
        
    finally:
        # 安全退出浏览器
        if driver:
            browser_manager.safe_quit(driver)

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\nWCL更新点击器执行成功！")
        else:
            print("\nWCL更新点击器执行失败！")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("用户中断程序执行")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行出现未预期错误: {e}")
        sys.exit(1)
