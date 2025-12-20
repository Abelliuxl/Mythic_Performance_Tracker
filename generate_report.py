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
from utils.report_manager import ReportManager
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

        # 创建报告管理器
        report_manager = ReportManager()

        # 生成HTML内容（不直接保存到文件）
        html_content = visualizer.generate_html_content_only(
            character_info_path=character_info_path,
            result_path=result_path
        )

        if html_content:
            # 使用报告管理器保存文件
            saved_path = report_manager.save_report(html_content)

            logger.success("HTML可视化报告生成成功!")
            logger.info(f"报告文件: {saved_path}")
            logger.info("请在浏览器中打开查看美观的可视化报告")

            # 显示文件统计信息
            stats = report_manager.get_file_stats()
            if stats:
                logger.info(f"当前文件统计: {stats['total_files']}个文件, {stats['total_size_mb']}MB")

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
