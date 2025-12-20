# Mythic Performance Tracker - 安装指南

[English](#english) | [中文](#中文)

---

## English

### Installation Guide

This guide will help you install and set up Mythic Performance Tracker on different platforms.

### Prerequisites

- Python 3.7 or higher
- Chrome browser
- ChromeDriver (included in the repository for Windows)

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/mythic-performance-tracker.git
cd mythic-performance-tracker
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 3. Platform-Specific Setup

##### Windows
- ChromeDriver is already included in the `chromedriver-win64/` directory
- No additional setup required

##### Linux
- Install Chrome browser:
```bash
# For Ubuntu/Debian
sudo apt-get update
sudo apt-get install google-chrome-stable

# For Fedora/CentOS
sudo dnf install google-chrome-stable
```

- Install ChromeDriver:
```bash
# Method 1: Using package manager
sudo apt-get install chromium-chromedriver  # For Ubuntu/Debian
sudo dnf install chromedriver              # For Fedora/CentOS

# Method 2: Download manually
# Download from https://chromedriver.chromium.org/downloads
# Extract and place in /usr/local/bin/
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

##### macOS
- Install Chrome browser from https://www.google.com/chrome/
- Install ChromeDriver:
```bash
# Method 1: Using Homebrew
brew install chromedriver

# Method 2: Download manually
# Download from https://chromedriver.chromium.org/downloads
# Extract and place in /usr/local/bin/
mv chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
```

#### 4. Configuration

Edit `config/settings.py` if needed:
- Update `WCL_ZONE_ID` for current season
- Adjust browser settings as needed
- Set proxy configuration if required

#### 5. Run the Application

```bash
python mplus_batch_crawler.py
```

### Troubleshooting

#### ChromeDriver Issues
If you encounter ChromeDriver issues:
1. Ensure ChromeDriver version matches your Chrome browser version
2. Check that ChromeDriver is in your PATH or in the correct directory
3. Try running with `--headless=false` to see browser output

#### Permission Issues
On Linux/macOS, ensure ChromeDriver has execute permissions:
```bash
chmod +x chromedriver
```

#### Proxy Issues
If using a proxy, ensure the proxy server is accessible and properly configured in `config/settings.py`

---

## 中文

### 安装指南

本指南将帮助您在不同平台上安装和设置 Mythic Performance Tracker。

### 前置要求

- Python 3.7 或更高版本
- Chrome 浏览器
- ChromeDriver（Windows 版本已包含在仓库中）

### 安装步骤

#### 1. 克隆仓库

```bash
git clone https://github.com/yourusername/mythic-performance-tracker.git
cd mythic-performance-tracker
```

#### 2. 安装依赖

```bash
pip install -r requirements.txt
```

#### 3. 平台特定设置

##### Windows
- ChromeDriver 已包含在 `chromedriver-win64/` 目录中
- 无需额外设置

##### Linux
- 安装 Chrome 浏览器：
```bash
# 对于 Ubuntu/Debian
sudo apt-get update
sudo apt-get install google-chrome-stable

# 对于 Fedora/CentOS
sudo dnf install google-chrome-stable
```

- 安装 ChromeDriver：
```bash
# 方法 1：使用包管理器
sudo apt-get install chromium-chromedriver  # 对于 Ubuntu/Debian
sudo dnf install chromedriver              # 对于 Fedora/CentOS

# 方法 2：手动下载
# 从 https://chromedriver.chromium.org/downloads 下载
# 解压并放置到 /usr/local/bin/
sudo mv chromedriver /usr/local/bin/
sudo chmod +x /usr/local/bin/chromedriver
```

##### macOS
- 从 https://www.google.com/chrome/ 安装 Chrome 浏览器
- 安装 ChromeDriver：
```bash
# 方法 1：使用 Homebrew
brew install chromedriver

# 方法 2：手动下载
# 从 https://chromedriver.chromium.org/downloads 下载
# 解压并放置到 /usr/local/bin/
mv chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
```

#### 4. 配置设置

如需要，编辑 `config/settings.py`：
- 更新当前赛季的 `WCL_ZONE_ID`
- 根据需要调整浏览器设置
- 如需要，设置代理配置

#### 5. 运行应用程序

```bash
python mplus_batch_crawler.py
```

### 故障排除

#### ChromeDriver 问题
如果遇到 ChromeDriver 问题：
1. 确保 ChromeDriver 版本与您的 Chrome 浏览器版本匹配
2. 检查 ChromeDriver 是否在您的 PATH 中或正确的目录中
3. 尝试使用 `--headless=false` 运行以查看浏览器输出

#### 权限问题
在 Linux/macOS 上，确保 ChromeDriver 有执行权限：
```bash
chmod +x chromedriver
```

#### 代理问题
如果使用代理，确保代理服务器可访问并在 `config/settings.py` 中正确配置

### 平台特定说明

#### Windows
- 使用 `chromedriver-win64/chromedriver.exe`
- 支持相对路径查找
- 自动检测 Chrome 浏览器安装位置

#### Linux
- 支持 Chrome 和 Chromium 浏览器
- 在多个常见路径中查找 ChromeDriver
- 自动处理系统路径和用户路径

#### macOS
- 支持 Chrome 和 Edge 浏览器
- 自动检测应用程序目录
- 支持 Homebrew 安装的 ChromeDriver

### 开发环境设置

如果您想为项目做贡献：

```bash
# 安装开发依赖
pip install -e .[dev]

# 运行测试
pytest

# 代码格式化
black .

# 代码检查
flake8 .
