"""
首次登录引导脚本 - 跨平台（Windows/Linux/macOS）

在有显示器的电脑上运行一次，手动登录战网获取 Cookie（cookies.pkl）。
之后 NAS 上的爬虫即可复用此 Cookie 登录态，无需转移整个 Chrome 配置目录。

用法:
  python login_helper.py

流程:
  1. 浏览器自动打开到战网登录页面
  2. 手动完成登录（输入账号密码/扫码）
  3. 登录成功后页面跳转到角色页面
  4. 回到终端，按 Enter 确认
  5. Cookie 自动提取保存到 chrome_profile/cookies.pkl
  6. 把 cookie 文件传到 NAS 上即可
"""

import sys
import os
import time
import pickle

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.browser_manager import BrowserManager


def main():
    print("=" * 60)
    print("    战网登录引导 - Mythic Performance Tracker")
    print("=" * 60)
    print()
    print("本脚本将打开浏览器。请完成战网登录后回到终端确认。")
    print()

    browser_manager = BrowserManager()
    driver = None
    try:
        print("正在启动浏览器...")
        driver = browser_manager.create_driver(
            use_persistent_session=False, headless=False
        )

        print("正在打开战网登录页面...")
        driver.get("https://wow.blizzard.cn/character/")
        time.sleep(2)

        print()
        print("=" * 60)
        print("  请在浏览器中完成战网登录。")
        print("  登录后页面会跳转到角色页面。")
        print("  看到角色页面后，回到这里确认。")
        print("=" * 60)
        input("  >> 按 Enter 确认已登录... ")

        time.sleep(2)

        current_url = driver.current_url
        if "login" in current_url.lower():
            print()
            print("⚠️  页面似乎还在登录页，Cookie 可能未生成。")
            retry = input("  按 Enter 重试，输入 q 退出: ")
            if retry.lower() == "q":
                return
            input("  >> 请完成登录后按 Enter... ")
            time.sleep(2)

        all_cookies = driver.get_cookies()
        blz_cookies = [
            c
            for c in all_cookies
            if any(
                d in (c.get("domain", "") or "").lower()
                for d in [
                    "blizzard.cn",
                    "battlenet.com.cn",
                    "battlenet.cn",
                    "webapi.blizzard.cn",
                    "wow.blizzard.cn",
                ]
            )
        ]

        print()
        print(f"  共获取 {len(all_cookies)} 个 Cookie")
        print(f"  其中 Blizzard 相关 {len(blz_cookies)} 个")
        for c in blz_cookies[:10]:
            print(f"    {c.get('domain', ''):40s} {c.get('name', ''):30s}")

        save_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "chrome_profile"
        )
        os.makedirs(save_dir, exist_ok=True)
        cookie_file = os.path.join(save_dir, "cookies.pkl")
        with open(cookie_file, "wb") as f:
            pickle.dump(blz_cookies if blz_cookies else all_cookies, f)

        print(f"\n  ✅ Cookie 已保存到: {cookie_file}")

        if blz_cookies:
            print("  ✅ 登录成功！现在可以把这个 cookies.pkl 文件")
            print("     传到 NAS 上的 chrome_profile/ 目录，然后运行爬虫。")
        else:
            print("  ⚠️  未找到 Blizzard 相关 Cookie，可能登录未成功。")
            print("     请重新运行此脚本并确保完成登录。")

    except Exception as e:
        print(f"\n  ❌ 出错: {e}")
        import traceback

        traceback.print_exc()
    finally:
        if driver:
            try:
                driver.quit()
            except Exception:
                pass
        print()
        input("  按 Enter 退出...")


if __name__ == "__main__":
    main()
