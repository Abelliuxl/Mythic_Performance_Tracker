<div align="center">

# Mythic Performance Tracker

</div>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.7%2B-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Active-green.svg)](https://github.com/Abelliuxl/mythic-performance-tracker)

</div>

<div align="center">

![Mythic Performance Tracker Logo](https://img.shields.io/badge/Mythic%2B-Performance%20Tracker-purple?style=for-the-badge&logo=world-of-warcraft&logoColor=white)

**A powerful tool for tracking and analyzing Mythic+ dungeon performance in World of Warcraft**

[English](#english) | [中文](#中文)

</div>

---

## English

### 🎯 Overview

Mythic Performance Tracker is a comprehensive Windows-based tool designed to crawl, process, and visualize Mythic+ dungeon performance data from Warcraft Logs (WCL). It provides detailed insights into player performance across different dungeons, levels, and classes.

### ✨ Features

- **🕷️ Web Crawling**: Automated data collection from Warcraft Logs
- **📊 Data Processing**: Comprehensive analysis of dungeon runs
- **📈 Visualization**: Beautiful HTML reports with interactive charts
- **🎨 Color Coding**: Class-specific and level-based color schemes
- **📱 Responsive Design**: Works on desktop and mobile devices
- **🔄 Real-time Updates**: Generates timestamped reports

### 🚀 Installation

#### Prerequisites

- Python 3.7 or higher
- Chrome browser
- [ChromeDriver](https://chromedriver.chromium.org/downloads) (included in the repository)

#### Setup

1. Clone the repository:
```bash
git clone https://github.com/Abelliuxl/Mythic_Performance_Tracker.git
cd mythic-performance-tracker
```

2. Install required dependencies:
```bash
pip install -r requirements.txt
```

3. Configure settings in `config/settings.py`:
   - Update `WCL_ZONE_ID` for current season
   - Adjust browser settings as needed
   - Set file paths

### 📝 Usage

1. Prepare your character data in `data/character_info.xlsx` with columns:
   - 玩家/Player
   - 角色名/Character Name
   - 服务器/Server
   - 职业/Class

2. Run the crawler:
```bash
python mplus_batch_crawler.py
```

3. View generated reports:
   - Excel report: `data/result.xlsx`
   - HTML visualization: `reports/mythic_performance_report_latest.html`

### 📁 Project Structure

```
Mythic_Performance_Tracker/
├── mplus_batch_crawler.py          # Main crawler script
├── config/
│   ├── __init__.py
│   └── settings.py                # Configuration settings
├── data/
│   ├── character_info.xlsx        # Input character data
│   └── result.xlsx               # Generated results
├── reports/
│   └── mythic_performance_report_latest.html  # HTML report
├── utils/
│   ├── __init__.py
│   ├── browser_manager.py        # Browser automation
│   ├── data_processor.py         # Data processing logic
│   ├── html_visualizer.py       # HTML report generation
│   ├── logger.py                 # Logging system
│   └── report_generator.py       # Excel report generation
├── chromedriver-win64/           # ChromeDriver executable
├── logs/                        # Log files
└── legacy/                      # Legacy code
```

### 🔧 Configuration

Key settings in `config/settings.py`:

- **DUNGEON_NAME_MAP**: Maps dungeon names between English and Chinese
- **DUNGEON_TIME_LIMIT**: Time limits for each dungeon
- **CLASS_COLOR_MAP**: Color codes for each class
- **BROWSER_CONFIG**: ChromeDriver and browser settings
- **CRAWLER_CONFIG**: Crawler behavior settings

### 📊 Report Features

The generated HTML reports include:

- **Summary Table**: Overview of all characters' performance
- **Character Statistics**: Individual player performance metrics
- **Dungeon Statistics**: Dungeon-specific analytics
- **Visual Charts**: Interactive charts showing:
  - Level distribution
  - Class performance
  - Dungeon completion rates

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<div align="center">

### 🙏 Acknowledgments

</div>

- Warcraft Logs API for providing performance data
- Chart.js for beautiful data visualization
- BeautifulSoup for HTML parsing

---

## 中文

### 🎯 项目概述

Mythic Performance Tracker 是一个基于 Windows 的强大工具，专门用于从 Warcraft Logs (WCL) 爬取、处理和可视化神话副本（Mythic+）的性能数据。它提供了不同副本、层数和职业的玩家表现详细分析。

### ✨ 主要功能

- **🕷️ 网页爬取**: 从 Warcraft Logs 自动收集数据
- **📊 数据处理**: 全面分析副本运行数据
- **📈 可视化报告**: 生成美观的 HTML 报告，包含交互式图表
- **🎨 颜色编码**: 职业专属和等级基础的颜色方案
- **📱 响应式设计**: 在桌面和移动设备上都能良好显示
- **🔄 实时更新**: 生成带时间戳的报告

### 🚀 安装说明

#### 前置要求

- Python 3.7 或更高版本
- Chrome 浏览器
- [ChromeDriver](https://chromedriver.chromium.org/downloads)（已包含在仓库中）

#### 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/Abelliuxl/Mythic_Performance_Tracker.git
cd mythic-performance-tracker
```

2. 安装依赖包：
```bash
pip install -r requirements.txt
```

3. 在 `config/settings.py` 中配置设置：
   - 更新当前赛季的 `WCL_ZONE_ID`
   - 根据需要调整浏览器设置
   - 设置文件路径

### 📝 使用方法

1. 准备角色数据文件 `data/character_info.xlsx`，包含以下列：
   - 玩家/Player
   - 角色名/Character Name
   - 服务器/Server
   - 职业/Class

2. 运行爬虫：
```bash
python mplus_batch_crawler.py
```

3. 查看生成的报告：
   - Excel 报告：`data/result.xlsx`
   - HTML 可视化报告：`reports/mythic_performance_report_latest.html`

### 📁 项目结构

```
Mythic_Performance_Tracker/
├── mplus_batch_crawler.py          # 主爬虫脚本
├── config/
│   ├── __init__.py
│   └── settings.py                # 配置设置
├── data/
│   ├── character_info.xlsx        # 输入的角色数据
│   └── result.xlsx               # 生成的结果
├── reports/
│   └── mythic_performance_report_latest.html  # HTML 报告
├── utils/
│   ├── __init__.py
│   ├── browser_manager.py        # 浏览器自动化
│   ├── data_processor.py         # 数据处理逻辑
│   ├── html_visualizer.py       # HTML 报告生成
│   ├── logger.py                 # 日志系统
│   └── report_generator.py       # Excel 报告生成
├── chromedriver-win64/           # ChromeDriver 可执行文件
├── logs/                        # 日志文件
└── legacy/                      # 旧版代码
```

### 🔧 配置说明

`config/settings.py` 中的主要设置：

- **DUNGEON_NAME_MAP**: 副本名称中英文映射
- **DUNGEON_TIME_LIMIT**: 每个副本的限时阈值
- **CLASS_COLOR_MAP**: 各职业的颜色代码
- **BROWSER_CONFIG**: ChromeDriver 和浏览器设置
- **CRAWLER_CONFIG**: 爬虫行为设置

### 📊 报告功能

生成的 HTML 报告包含：

- **总览表格**: 所有角色表现的概览
- **角色统计**: 单个玩家的性能指标
- **副本统计**: 副本特定的分析数据
- **可视化图表**: 交互式图表展示：
  - 等级分布
  - 职业表现
  - 副本完成率

### 🤝 贡献指南

1. Fork 仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开 Pull Request

### 📄 许可证

本项目采用 MIT 许可证 - 详情请查看 [LICENSE](LICENSE) 文件。

### 🙏 致谢

- Warcraft Logs API 提供性能数据
- Chart.js 提供美观的数据可视化
- BeautifulSoup 提供 HTML 解析功能

---

<div align="center">

**Made with ❤️ by Mythic Performance Tracker Team**

[![GitHub stars](https://img.shields.io/github/stars/Abelliuxl/mythic-performance-tracker?style=social)](https://github.com/Abelliuxl/mythic-performance-tracker)
[![GitHub forks](https://img.shields.io/github/forks/Abelliuxl/mythic-performance-tracker?style=social)](https://github.com/Abelliuxl/mythic-performance-tracker)

</div>
