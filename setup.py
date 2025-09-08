"""
Mythic Performance Tracker Setup Script
用于跨平台安装和配置
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# 读取requirements文件
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mythic-performance-tracker",
    version="1.0.0",
    author="Mythic Performance Tracker Team",
    author_email="your.email@example.com",
    description="A powerful tool for tracking and analyzing Mythic+ dungeon performance in World of Warcraft",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/mythic-performance-tracker",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Games/Entertainment",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.2.4",
            "black>=21.0.0",
            "flake8>=3.9.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "mythic-tracker=mplus_batch_crawler:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.xlsx", "*.txt", "*.md", "*.html"],
    },
    data_files=[
        ("config", ["config/settings.py"]),
        ("data", ["data/character_info.xlsx", "data/result.xlsx"]),
        ("logs", ["logs/crawl_log.txt"]),
        ("reports", ["reports/mythic_performance_report_latest.html"]),
        ("utils", ["utils/*.py"]),
    ],
    zip_safe=False,
)
