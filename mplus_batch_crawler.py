import time
import sys
import os
import json
import pickle
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import (
    FILE_PATHS, CRAWLER_CONFIG, SERVER_SLUG_MAP,
    SESSION_CONFIG
)
from utils.logger import logger
from utils.data_processor import DataProcessor
from utils.report_generator import ReportGenerator
from utils.browser_manager import BrowserManager
from utils.html_visualizer import HTMLVisualizer


class MythicPlusCrawler:
    def __init__(self):
        self.data_processor = DataProcessor()
        self.report_generator = ReportGenerator()
        self.browser_manager = BrowserManager()
        self.config = CRAWLER_CONFIG
        self.cookie_file = os.path.join(
            os.getcwd(),
            SESSION_CONFIG.get("user_data_dir", "chrome_profile"),
            "cookies.pkl"
        )

    def _ensure_login(self, driver):
        logger.info("检查登录状态...")
        try:
            driver.get("https://wow.blizzard.cn/character/")
            time.sleep(5)
            current = driver.current_url.lower()
            if "login" in current:
                logger.info("尝试注入 Cookie 恢复登录态...")
                injected = self.browser_manager.inject_cookies(driver)
                if injected:
                    driver.get("https://wow.blizzard.cn/character/")
                    time.sleep(5)
                    if "login" not in driver.current_url.lower():
                        self._save_cookies(driver)
                        logger.success("Cookie 注入成功，已恢复登录态")
                        return True

                logger.warning(
                    "需要登录战网才能爬取。\n"
                    "请在有显示器的电脑上运行:\n"
                    "  python login_helper.py\n"
                    "登录完成后，把生成的 chrome_profile/cookies.pkl 拷贝到本机同目录。"
                )
                return False
            logger.success("已检测到登录态")
            self._save_cookies(driver)
            return True
        except Exception as e:
            logger.error(f"检查登录态失败: {e}")
            return False

    def _save_cookies(self, driver):
        try:
            cookies = driver.get_cookies()
            os.makedirs(os.path.dirname(self.cookie_file), exist_ok=True)
            with open(self.cookie_file, "wb") as f:
                pickle.dump(cookies, f)
            logger.info(f"已保存 {len(cookies)} 个 Cookie 到 {self.cookie_file}")
        except Exception as e:
            logger.debug(f"保存 Cookie 失败: {e}")

    def scrape_character(self, driver, server_name, character_name):
        url = self.data_processor.build_character_url(server_name, character_name)
        max_attempts = self.config.get("max_attempts", 3)
        wait_time = self.config.get("wait_time", 8)

        for attempt in range(1, max_attempts + 1):
            logger.info(f"正在加载角色页面 (第 {attempt} 次): {url}")
            try:
                driver.get(url)
                time.sleep(wait_time)

                self.browser_manager.stop_page_loading(driver)

                all_records = []

                records = self.data_processor.extract_mplus_from_dom(driver)
                if records:
                    all_records.extend(records)

                if not all_records:
                    records = self.data_processor.extract_mplus_from_page_text(driver)
                    if records:
                        logger.info(f"从页面文本提取到 {len(records)} 条大秘境记录")
                        all_records.extend(records)

                if not all_records:
                    vue_records = self.data_processor.extract_window_data_vue(driver)
                    if vue_records:
                        logger.info(f"从 Vue data 提取到 {len(vue_records)} 条记录")
                        all_records.extend(vue_records)

                if not all_records:
                    attr_records = self.data_processor.extract_json_from_attrs(driver)
                    if attr_records:
                        logger.info(f"从 DOM 属性提取到 {len(attr_records)} 条记录")
                        all_records.extend(attr_records)

                if not all_records:
                    vuex_records = self.data_processor.extract_vuex_data(driver)
                    if vuex_records:
                        logger.info(f"从 Vuex store 提取到 {len(vuex_records)} 条记录")
                        all_records.extend(vuex_records)

                if all_records:
                    self._save_cookies(driver)
                    return all_records

                if attempt == 1:
                    page_source = driver.page_source[:3000]
                    logger.info(f"页面源码片段: {page_source}")

            except Exception as e:
                logger.error(f"第 {attempt} 次加载页面失败: {e}")

            if attempt < max_attempts:
                time.sleep(3)

        logger.warning(f"未能提取到数据: {character_name}")
        return []

    def run_crawler(self):
        logger.info("=== 开始执行神话副本爬虫 (Blizzard 国服) ===")

        char_df = self.data_processor.load_character_data(FILE_PATHS["character_info"])
        if char_df is None:
            logger.error("无法加载角色数据，程序终止")
            return False

        if not self.data_processor.validate_character_data(char_df):
            logger.error("角色数据验证失败，程序终止")
            return False

        all_records = []
        driver = None

        try:
            driver = self.browser_manager.create_driver(use_persistent_session=False)

            if not self._ensure_login(driver):
                return False

            for _, row in char_df.iterrows():
                player = str(row["玩家"]).strip()
                name = str(row["角色名"]).strip()
                server = str(row["服务器"]).strip()

                logger.info(f"\n—— 开始抓取：{player} / {name}（{server}）")

                char_data = self.scrape_character(driver, server, name)
                if char_data:
                    logger.info(f"获取成功，共 {len(char_data)} 条记录")
                else:
                    logger.warning(f"未获取到数据: {name}")

                for entry in char_data:
                    entry.update({
                        "玩家": player,
                        "角色名": name,
                        "服务器": server,
                    })
                    all_records.append(entry)

            self._save_cookies(driver)

        except Exception as e:
            logger.error(f"爬取过程出错: {e}")
            import traceback
            logger.debug(traceback.format_exc())
        finally:
            if driver:
                self.browser_manager.safe_quit(driver)

        if not all_records:
            logger.error("没有任何副本数据被抓取，终止。")
            return False

        return self._generate_report(all_records, char_df)

    def _generate_report(self, all_records, char_df):
        try:
            df = self.report_generator.prepare_dataframe(all_records)
            if df is None:
                return False

            excel_success = self.report_generator.generate_excel_report(
                df, char_df, FILE_PATHS["result"]
            )
            if not excel_success:
                logger.error("Excel报告生成失败")
                return False

            logger.info("正在生成HTML可视化报告...")
            html_visualizer = HTMLVisualizer()
            os.makedirs("reports", exist_ok=True)

            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_output_path = f"reports/mythic_performance_report_{timestamp}.html"

            html_success = html_visualizer.generate_html_report(
                character_info_path=FILE_PATHS["character_info"],
                result_path=FILE_PATHS["result"],
                output_path=html_output_path
            )

            if html_success:
                import shutil
                latest_path = "reports/mythic_performance_report_latest.html"
                shutil.copy2(html_output_path, latest_path)
                logger.success(f"HTML可视化报告生成成功: {html_output_path}")
                logger.success(f"最新版本副本: {latest_path}")
                logger.info("=== 爬虫执行完成 ===")
                return True
            else:
                logger.error("HTML报告生成失败")
                return False

        except Exception as e:
            logger.error(f"生成报告失败: {e}")
            import traceback
            logger.debug(traceback.format_exc())
            return False

    def cleanup(self):
        try:
            logger.save_to_file()
        except Exception as e:
            logger.error(f"清理资源失败: {e}")


def main():
    crawler = MythicPlusCrawler()
    try:
        success = crawler.run_crawler()
        if success:
            print("\n爬虫执行成功！")
        else:
            print("\n爬虫执行失败！")
            sys.exit(1)
    except KeyboardInterrupt:
        logger.warning("用户中断程序执行")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行出现未预期错误: {e}")
        sys.exit(1)
    finally:
        crawler.cleanup()


if __name__ == "__main__":
    main()
