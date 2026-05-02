import time
import sys
import os
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import FILE_PATHS, CRAWLER_CONFIG, WCL_ZONE_ID
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
    
    def scrape_character(self, driver, server, character_name):
        """爬取单个角色数据"""
        url = self.data_processor.build_wcl_url(server, character_name)
        max_attempts = self.config.get("max_attempts", 3)
        wait_time = self.config.get("wait_time", 6)
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"正在加载（尝试第 {attempt} 次）：{url}")
            
            try:
                driver.get(url)
                time.sleep(wait_time)
                
                # 停止页面加载
                self.browser_manager.stop_page_loading(driver)
                
                # 解析页面
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                rows = soup.find_all("tr", {"role": "row"})
                
                if rows:
                    logger.info(f"表格成功获取，共 {len(rows)} 行")
                    return self._parse_character_data(rows)
                else:
                    logger.warning(f"第 {attempt} 次未找到表格内容")
                    
            except Exception as e:
                logger.error(f"尝试第 {attempt} 次加载页面失败：{e}")
            
            # 如果不是最后一次尝试，等待一段时间
            if attempt < max_attempts:
                time.sleep(2)
        
        logger.error(f"页面多次加载未成功，跳过角色：{character_name}")
        return []
    
    def _parse_character_data(self, rows):
        """解析角色数据"""
        records = []
        
        for row in rows:
            try:
                record = self.data_processor.parse_dungeon_data(row)
                if record:
                    records.append(record)
            except Exception as e:
                logger.error(f"解析副本行失败：{e}")
                continue
        
        return records
    
    def run_crawler(self):
        """运行爬虫主程序"""
        logger.info("=== 开始执行神话副本爬虫 ===")
        
        # 加载角色数据
        char_df = self.data_processor.load_character_data(FILE_PATHS["character_info"])
        if char_df is None:
            logger.error("无法加载角色数据，程序终止")
            return False
        
        # 验证角色数据
        if not self.data_processor.validate_character_data(char_df):
            logger.error("角色数据验证失败，程序终止")
            return False
        
        all_records = []
        
        # 遍历角色进行爬取
        for _, row in char_df.iterrows():
            player = str(row["玩家"]).strip()
            name = str(row["角色名"]).strip()
            server = str(row["服务器"]).strip()
            
            logger.info(f"\n—— 开始抓取：{player} / {name}（{server}）")
            
            driver = None
            try:
                # 创建浏览器驱动
                driver = self.browser_manager.create_driver()
                
                # 爬取角色数据
                char_data = self.scrape_character(driver, server, name)
                logger.info(f"获取成功，共 {len(char_data)} 条记录")
                
                # 添加角色信息到记录
                for entry in char_data:
                    entry.update({
                        "玩家": player,
                        "角色名": name,
                        "服务器": server
                    })
                    all_records.append(entry)
                    
            except Exception as e:
                logger.error(f"抓取失败：{name}：{e}")
                
            finally:
                # 安全退出浏览器
                if driver:
                    self.browser_manager.safe_quit(driver)
        
        # 生成报告
        if not all_records:
            logger.error("没有任何副本数据被抓取，终止写入。")
            return False
        
        return self._generate_report(all_records, char_df)
    
    def _generate_report(self, all_records, char_df):
        """生成报告"""
        try:
            # 准备数据框
            df = self.report_generator.prepare_dataframe(all_records)
            if df is None:
                return False
            
            # 生成Excel报告
            excel_success = self.report_generator.generate_excel_report(
                df, char_df, FILE_PATHS["result"]
            )
            
            if not excel_success:
                logger.error("Excel报告生成失败")
                return False
            
            # 自动生成HTML可视化报告
            logger.info("正在生成HTML可视化报告...")
            html_visualizer = HTMLVisualizer()
            
            # 确保reports目录存在
            os.makedirs("reports", exist_ok=True)
            
            # 生成带时间戳的HTML报告
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            html_output_path = f"reports/mythic_performance_report_{timestamp}.html"
            
            html_success = html_visualizer.generate_html_report(
                character_info_path=FILE_PATHS["character_info"],
                result_path=FILE_PATHS["result"],
                output_path=html_output_path
            )
            
            if html_success:
                # 同时生成最新版本副本
                latest_path = "reports/mythic_performance_report_latest.html"
                import shutil
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
            return False
    
    def cleanup(self):
        """清理资源"""
        try:
            # 保存日志
            logger.save_to_file()
        except Exception as e:
            logger.error(f"清理资源失败: {e}")

def main():
    """主函数"""
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
