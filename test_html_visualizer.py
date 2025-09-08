#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试HTML可视化生成器
"""

import os
from utils.html_visualizer import HTMLVisualizer
from utils.logger import logger

def test_html_visualization():
    """测试HTML可视化功能"""
    logger.info("开始测试HTML可视化生成器...")
    
    # 文件路径
    character_info_path = "data/character_info.xlsx"
    result_path = "data/result.xlsx"
    output_path = "mythic_performance_report.html"
    
    # 检查输入文件是否存在
    if not os.path.exists(character_info_path):
        logger.error(f"角色信息文件不存在: {character_info_path}")
        return False
    
    if not os.path.exists(result_path):
        logger.error(f"结果文件不存在: {result_path}")
        return False
    
    # 创建HTML可视化器
    visualizer = HTMLVisualizer()
    
    # 生成HTML报告
    success = visualizer.generate_html_report(
        character_info_path=character_info_path,
        result_path=result_path,
        output_path=output_path
    )
    
    if success:
        logger.success(f"HTML报告生成成功: {output_path}")
        logger.info("请在浏览器中打开生成的HTML文件查看可视化报告")
        return True
    else:
        logger.error("HTML报告生成失败")
        return False

if __name__ == "__main__":
    test_html_visualization()
