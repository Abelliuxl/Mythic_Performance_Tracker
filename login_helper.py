"""
首次登录引导脚本
在有显示器的电脑上运行一次，登录战网后即会自动保存登录态。

用法:
  python login_helper.py

登录成功后关闭浏览器，之后 crawler 就会复用此登录会话。
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.browser_manager import BrowserManager
from utils.logger import logger


def main():
    print("=" * 60)
    print("   战网登录引导 - Mythic Performance Tracker")
    print("=" * 60)
    print()
    print("本脚本将打开浏览器，请完成战网登录。")
    print("登录成功后，请保持浏览器开着运行一会儿确保会话稳定。")
    print("之后关闭浏览器即可，登录态会自动保存。")
    print()

    browser_manager = BrowserManager()
    driver = None

    try:
        driver = browser_manager.create_driver(use_persistent_session=True)

        print("正在打开战网登录页面...")
        driver.get("https://wow.blizzard.cn/character/")
        print()
        print("请在浏览器中完成战网登录。")
        print("登录后页面会跳转到角色页面。")
        print()
        print("看到角色页面后，在此按 Enter 键确认登录成功...")
        input(">> ")

        current_url = driver.current_url
        if "login" in current_url.lower():
            print("似乎还在登录页面，请确认已成功登录。")
            again = input("按 Enter 重试，输入 q 退出: ")
            if again.lower() == "q":
                print("退出登录引导。")
                return
        else:
            print(f"登录成功! 当前URL: {current_url}")
            print("登录会话已保存在 chrome_profile/ 目录。")

        print()
        print("你可以关闭浏览器了。之后运行爬虫即可复用此登录态。")

    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        logger.error(f"登录引导失败: {e}")
    finally:
        if driver:
            browser_manager.safe_quit(driver)


if __name__ == "__main__":
    main()
