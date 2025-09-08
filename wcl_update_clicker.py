import time
import sys
import os
import pandas as pd
from urllib.parse import quote
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, StaleElementReferenceException

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import FILE_PATHS, BROWSER_CONFIG, WCL_BASE_URL, WCL_ZONE_ID
from utils.logger import logger
from utils.browser_manager import BrowserManager

def build_wcl_url(server, character_name):
    """构建WCL URL"""
    return f"{WCL_BASE_URL}/character/cn/{quote(server.strip(), safe='')}/{quote(character_name.strip(), safe='')}?zone={WCL_ZONE_ID}"

def click_update_with_retry(driver, url, max_attempts=3):
    """重试机制点击Update按钮，使用多种点击策略"""
    for attempt in range(1, max_attempts + 1):
        try:
            driver.get(url)
            
            # 等待页面加载完成
            wait = WebDriverWait(driver, 10)
            time.sleep(3)  # 额外等待页面稳定
            
            # 尝试多种点击策略
            success = False
            
            # 策略2：使用JavaScript点击
            if not success:
                try:
                    update_button = wait.until(EC.presence_of_element_located((By.ID, "update-link")))
                    driver.execute_script("arguments[0].click();", update_button)
                    logger.success(f"策略2成功：JavaScript点击 Update（第 {attempt} 次）：{url}")
                    success = True
                except Exception as e:
                    logger.info(f"策略2失败：{e}")
            
            # 策略1：直接点击
            if not success:
                try:
                    update_button = wait.until(EC.element_to_be_clickable((By.ID, "update-link")))
                    update_button.click()
                    logger.success(f"策略1成功：直接点击 Update（第 {attempt} 次）：{url}")
                    success = True
                except Exception as e:
                    logger.info(f"策略1失败：{e}")
            
            # 策略3：使用ActionChains
            if not success:
                try:
                    update_button = wait.until(EC.element_to_be_clickable((By.ID, "update-link")))
                    actions = ActionChains(driver)
                    actions.move_to_element(update_button).click().perform()
                    logger.success(f"策略3成功：ActionChains点击 Update（第 {attempt} 次）：{url}")
                    success = True
                except Exception as e:
                    logger.info(f"策略3失败：{e}")
            
            # 策略4：先隐藏拦截元素，再点击
            if not success:
                try:
                    # 尝试隐藏可能拦截的登录链接
                    driver.execute_script("""
                        var signInLinks = document.querySelectorAll('a.header-bottom-bar__item--sign-in');
                        signInLinks.forEach(function(link) {
                            link.style.display = 'none';
                        });
                    """)
                    
                    # 等待一下，然后点击
                    time.sleep(1)
                    update_button = wait.until(EC.element_to_be_clickable((By.ID, "update-link")))
                    update_button.click()
                    logger.success(f"策略4成功：隐藏拦截元素后点击 Update（第 {attempt} 次）：{url}")
                    success = True
                except Exception as e:
                    logger.info(f"策略4失败：{e}")
                    # 恢复登录链接显示
                    driver.execute_script("""
                        var signInLinks = document.querySelectorAll('a.header-bottom-bar__item--sign-in');
                        signInLinks.forEach(function(link) {
                            link.style.display = '';
                        });
                    """)
            
            # 策略5：滚动到元素位置再点击
            if not success:
                try:
                    update_button = wait.until(EC.presence_of_element_located((By.ID, "update-link")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", update_button)
                    time.sleep(1)
                    update_button.click()
                    logger.success(f"策略5成功：滚动后点击 Update（第 {attempt} 次）：{url}")
                    success = True
                except Exception as e:
                    logger.info(f"策略5失败：{e}")
            
            if success:
                time.sleep(2)
                return True
            else:
                logger.warning(f"所有策略都失败（第 {attempt} 次）：{url}")
                time.sleep(2)
        
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
            
            # 添加重试机制
            max_retries = 3
            for retry in range(max_retries):
                try:
                    success = click_update_with_retry(driver, url)
                    if success:
                        break
                    elif retry < max_retries - 1:
                        logger.info(f"准备重试角色：{name}（{server}）")
                        time.sleep(3)  # 重试前等待
                except Exception as e:
                    logger.error(f"处理角色 {name} 时出现错误：{e}")
                    if retry < max_retries - 1:
                        logger.info(f"准备重试角色：{name}（{server}）")
                        time.sleep(3)  # 重试前等待
                    continue
        
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
