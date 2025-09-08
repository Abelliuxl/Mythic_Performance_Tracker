#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Mythic+ 性能追踪报告生成器
在爬虫完成后自动生成美观的HTML可视化报告
"""

import os
import sys
from datetime import datetime
from utils.html_visualizer import HTMLVisualizer
from utils.logger import logger

def generate_html_report():
    """
    生成HTML可视化报告
    在爬虫完成后调用此函数自动生成报告
    """
    logger.info("开始生成Mythic+性能可视化报告...")
    
    # 文件路径配置
    character_info_path = "data/character_info.xlsx"
    result_path = "data/result.xlsx"
    
    # 生成带时间戳的输出文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"reports/mythic_performance_report_{timestamp}.html"
    
    # 确保reports目录存在
    os.makedirs("reports", exist_ok=True)
    
    # 检查输入文件是否存在
    if not os.path.exists(character_info_path):
        logger.error(f"角色信息文件不存在: {character_info_path}")
        logger.info("请先运行爬虫生成数据文件")
        return False
    
    if not os.path.exists(result_path):
        logger.error(f"结果文件不存在: {result_path}")
        logger.info("请先运行爬虫生成数据文件")
        return False
    
    try:
        # 创建HTML可视化器
        visualizer = HTMLVisualizer()
        
        # 生成HTML报告
        success = visualizer.generate_html_report(
            character_info_path=character_info_path,
            result_path=result_path,
            output_path=output_path
        )
        
        if success:
            logger.success(f"HTML可视化报告生成成功!")
            logger.info(f"报告文件: {output_path}")
            logger.info("请在浏览器中打开查看美观的可视化报告")
            
            # 同时生成一个最新版本的副本（不带时间戳）
            latest_path = "reports/mythic_performance_report_latest.html"
            import shutil
            shutil.copy2(output_path, latest_path)
            logger.info(f"最新版本副本: {latest_path}")
            
            return True
        else:
            logger.error("HTML报告生成失败")
            return False
            
    except Exception as e:
        logger.error(f"生成报告时发生错误: {e}")
        return False

def main():
    """主函数"""
    print("=" * 60)
    print("Mythic+ 性能追踪报告生成器")
    print("=" * 60)
    
    success = generate_html_report()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ 报告生成完成!")
        print("📁 报告文件位置: reports/")
        print("🌐 在浏览器中打开HTML文件查看可视化报告")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ 报告生成失败!")
        print("请检查数据文件是否存在且格式正确")
        print("=" * 60)
        sys.exit(1)

if __name__ == "__main__":
    main()
