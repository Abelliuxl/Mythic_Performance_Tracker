#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML报告文件管理器
负责管理报告文件的生成、清理、压缩和组织
"""

import os
import shutil
import gzip
import glob
from datetime import datetime, timedelta
from pathlib import Path
from config.settings import REPORT_CONFIG
from utils.logger import logger

class ReportManager:
    """HTML报告文件管理器"""

    def __init__(self):
        self.config = REPORT_CONFIG
        self.output_dir = Path(self.config["output_dir"])
        self.output_dir.mkdir(exist_ok=True)

    def generate_report_path(self, timestamp=None):
        """
        生成报告文件路径
        支持按日期组织文件
        """
        if timestamp is None:
            timestamp = datetime.now()

        if self.config["organize_by_date"]:
            # 按日期组织：reports/2025-09-08/mythic_performance_report_220301.html
            date_dir = self.output_dir / timestamp.strftime("%Y-%m-%d")
            date_dir.mkdir(exist_ok=True)
            filename = f"mythic_performance_report_{timestamp.strftime('%H%M%S')}.html"
            return date_dir / filename
        else:
            # 原方式：reports/mythic_performance_report_20250908_220301.html
            filename = f"mythic_performance_report_{timestamp.strftime('%Y%m%d_%H%M%S')}.html"
            return self.output_dir / filename

    def save_report(self, content, timestamp=None):
        """
        保存报告文件
        返回保存的文件路径
        """
        report_path = self.generate_report_path(timestamp)

        # 写入文件
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"报告已保存: {report_path}")

        # 更新最新版本副本
        if self.config["keep_latest_copy"]:
            self._update_latest_copy(report_path)

        # 执行清理任务
        self._cleanup_old_files()

        return report_path

    def _update_latest_copy(self, source_path):
        """更新最新版本副本"""
        latest_path = self.output_dir / self.config["latest_filename"]

        try:
            shutil.copy2(source_path, latest_path)
            logger.info(f"最新版本副本已更新: {latest_path}")
        except Exception as e:
            logger.error(f"更新最新版本副本失败: {e}")

    def _cleanup_old_files(self):
        """清理旧文件"""
        try:
            # 获取所有HTML文件
            html_files = []
            for pattern in ["**/*.html", "**/*.html.gz"]:
                html_files.extend(self.output_dir.glob(pattern))

            if not html_files:
                return

            # 按修改时间排序（最新的在前）
            html_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

            # 分离压缩和未压缩文件
            compressed_files = [f for f in html_files if f.suffix == '.gz']
            uncompressed_files = [f for f in html_files if f.suffix == '.html']

            # 处理未压缩文件
            self._process_uncompressed_files(uncompressed_files)

            # 处理压缩文件
            self._process_compressed_files(compressed_files)

        except Exception as e:
            logger.error(f"清理文件时发生错误: {e}")

    def _process_uncompressed_files(self, files):
        """处理未压缩文件"""
        now = datetime.now()

        for i, file_path in enumerate(files):
            try:
                # 计算文件年龄
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                days_old = (now - file_mtime).days

                # 跳过最新版本副本
                if file_path.name == self.config["latest_filename"]:
                    continue

                # 如果超过最大文件数量，压缩或删除
                if i >= self.config["max_files"]:
                    if self.config["compress_old_files"] and days_old >= self.config["compress_after_days"]:
                        self._compress_file(file_path)
                    elif self.config["delete_after_days"] > 0 and days_old >= self.config["delete_after_days"]:
                        self._delete_file(file_path)
                # 即使在限制内，也检查是否需要压缩
                elif self.config["compress_old_files"] and days_old >= self.config["compress_after_days"]:
                    self._compress_file(file_path)

            except Exception as e:
                logger.error(f"处理文件 {file_path} 时发生错误: {e}")

    def _process_compressed_files(self, files):
        """处理压缩文件"""
        if self.config["delete_after_days"] <= 0:
            return

        now = datetime.now()

        for file_path in files:
            try:
                file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                days_old = (now - file_mtime).days

                # 删除过期的压缩文件
                if days_old >= self.config["delete_after_days"]:
                    self._delete_file(file_path)

            except Exception as e:
                logger.error(f"处理压缩文件 {file_path} 时发生错误: {e}")

    def _compress_file(self, file_path):
        """压缩文件"""
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')

            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # 删除原文件
            file_path.unlink()

            logger.info(f"文件已压缩: {compressed_path}")
            return True

        except Exception as e:
            logger.error(f"压缩文件 {file_path} 失败: {e}")
            return False

    def _delete_file(self, file_path):
        """删除文件"""
        try:
            file_path.unlink()
            logger.info(f"文件已删除: {file_path}")
            return True
        except Exception as e:
            logger.error(f"删除文件 {file_path} 失败: {e}")
            return False

    def get_file_stats(self):
        """获取文件统计信息"""
        try:
            # 获取所有HTML文件（包括压缩的）
            html_files = []
            for pattern in ["**/*.html", "**/*.html.gz"]:
                html_files.extend(self.output_dir.glob(pattern))

            total_files = len(html_files)
            total_size = sum(f.stat().st_size for f in html_files)

            # 按日期分组统计
            date_groups = {}
            for file_path in html_files:
                file_date = datetime.fromtimestamp(file_path.stat().st_mtime).date()
                if file_date not in date_groups:
                    date_groups[file_date] = []
                date_groups[file_date].append(file_path)

            return {
                "total_files": total_files,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "date_groups": {str(date): len(files) for date, files in date_groups.items()},
                "output_dir": str(self.output_dir)
            }

        except Exception as e:
            logger.error(f"获取文件统计信息失败: {e}")
            return None

    def list_recent_reports(self, days=7):
        """列出最近N天的报告"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days)

            html_files = []
            for pattern in ["**/*.html", "**/*.html.gz"]:
                html_files.extend(self.output_dir.glob(pattern))

            recent_files = []
            for file_path in html_files:
                if datetime.fromtimestamp(file_path.stat().st_mtime) >= cutoff_date:
                    recent_files.append({
                        "path": str(file_path),
                        "name": file_path.name,
                        "size": file_path.stat().st_size,
                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                        "is_compressed": file_path.suffix == '.gz'
                    })

            # 按修改时间排序
            recent_files.sort(key=lambda x: x["modified"], reverse=True)

            return recent_files

        except Exception as e:
            logger.error(f"列出最近报告失败: {e}")
            return []

    def cleanup_empty_dirs(self):
        """清理空目录"""
        try:
            for dir_path in sorted(self.output_dir.rglob("*"), key=lambda x: len(x.parts), reverse=True):
                if dir_path.is_dir() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    logger.info(f"删除空目录: {dir_path}")

        except Exception as e:
            logger.error(f"清理空目录失败: {e}")
