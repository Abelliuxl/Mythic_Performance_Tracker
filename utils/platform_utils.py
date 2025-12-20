"""
Platform-specific utilities for Mythic Performance Tracker
"""

import os
import sys
import platform
from pathlib import Path
from typing import Optional, Dict, Any
from utils.logger import logger

class PlatformUtils:
    """Platform detection and configuration utilities"""
    
    def __init__(self):
        self.platform = self._detect_platform()
        self.chromedriver_paths = self._get_chromedriver_paths()
        
    def _detect_platform(self) -> str:
        """Detect the current operating system"""
        system = platform.system().lower()
        
        if system == "windows":
            return "windows"
        elif system == "linux":
            return "linux"
        elif system == "darwin":
            return "macos"
        else:
            logger.warning(f"Unknown platform: {system}, defaulting to linux")
            return "linux"
    
    def get_platform(self) -> str:
        """Get the current platform name"""
        return self.platform
    
    def is_windows(self) -> bool:
        """Check if running on Windows"""
        return self.platform == "windows"
    
    def is_linux(self) -> bool:
        """Check if running on Linux"""
        return self.platform == "linux"
    
    def is_macos(self) -> bool:
        """Check if running on macOS"""
        return self.platform == "macos"
    
    def _get_chromedriver_paths(self) -> Dict[str, str]:
        """Get platform-specific ChromeDriver paths"""
        paths = {
            "windows": {
                "default": "chromedriver-win64/chromedriver.exe",
                "alt": "chromedriver.exe",
                "system": "chromedriver.exe"
            },
            "linux": {
                "default": "chromedriver-linux64/chromedriver",
                "alt": "chromedriver",
                "system": "/usr/local/bin/chromedriver",
                "home": os.path.expanduser("~/bin/chromedriver")
            },
            "macos": {
                "default": "chromedriver-mac-x64/chromedriver",
                "alt": "chromedriver",
                "system": "/usr/local/bin/chromedriver",
                "home": os.path.expanduser("~/bin/chromedriver")
            }
        }
        return paths.get(self.platform, paths["linux"])
    
    def get_chromedriver_path(self) -> Optional[str]:
        """Get the appropriate ChromeDriver path for the current platform"""
        paths = self.chromedriver_paths
        
        # Try default path first (project-specific)
        if os.path.exists(paths["default"]):
            logger.info(f"Using ChromeDriver from project path: {paths['default']}")
            return paths["default"]
        
        # Try alternative path in current directory
        if os.path.exists(paths["alt"]):
            logger.info(f"Using ChromeDriver from current directory: {paths['alt']}")
            return paths["alt"]
        
        # Try system path
        if os.path.exists(paths["system"]):
            logger.info(f"Using ChromeDriver from system path: {paths['system']}")
            return paths["system"]
        
        # Try home directory path (for Linux/macOS)
        if self.platform in ["linux", "macos"] and "home" in paths:
            if os.path.exists(paths["home"]):
                logger.info(f"Using ChromeDriver from home directory: {paths['home']}")
                return paths["home"]
        
        logger.error(f"ChromeDriver not found. Please install it or place it in one of these locations:")
        for path_name, path in paths.items():
            logger.error(f"  - {path_name}: {path}")
        
        return None
    
    def get_platform_config(self) -> Dict[str, Any]:
        """Get platform-specific configuration"""
        config = {
            "platform": self.platform,
            "file_separator": os.sep,
            "path_separator": os.pathsep,
            "line_ending": "\r\n" if self.is_windows() else "\n",
            "executable_extension": ".exe" if self.is_windows() else ""
        }
        
        # Platform-specific browser options
        browser_options = {
            "windows": {
                "headless_arg": "--headless",
                "gpu_arg": "--disable-gpu",
                "sandbox_arg": "--no-sandbox"
            },
            "linux": {
                "headless_arg": "--headless",
                "gpu_arg": "--disable-gpu",
                "sandbox_arg": "--no-sandbox",
                "xvfb_arg": "--disable-dev-shm-usage"
            },
            "macos": {
                "headless_arg": "--headless",
                "gpu_arg": "",
                "sandbox_arg": "--no-sandbox"
            }
        }
        
        config["browser_options"] = browser_options.get(self.platform, browser_options["linux"])
        
        return config
    
    def get_data_dir(self) -> str:
        """Get platform-appropriate data directory"""
        if self.is_windows():
            # Windows: Use AppData
            app_data = os.getenv('APPDATA')
            if app_data:
                return os.path.join(app_data, "MythicPerformanceTracker")
        
        # Linux/macOS: Use home directory
        home_dir = os.path.expanduser("~")
        return os.path.join(home_dir, ".mythic_performance_tracker")
    
    def ensure_directory(self, path: str) -> bool:
        """Ensure a directory exists, creating it if necessary"""
        try:
            os.makedirs(path, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {path}: {e}")
            return False
    
    def get_chrome_binary_path(self) -> Optional[str]:
        """Get Chrome browser binary path for the current platform"""
        if self.is_windows():
            # Windows Chrome paths
            possible_paths = [
                os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Google\\Chrome\\Application\\chrome.exe"),
                os.path.join(os.environ.get("PROGRAMFILES", ""), "Google\\Chrome\\Application\\chrome.exe"),
                os.path.join(os.environ.get("PROGRAMFILES(X86)", ""), "Microsoft\\Edge\\Application\\msedge.exe"),
                os.path.join(os.environ.get("PROGRAMFILES", ""), "Microsoft\\Edge\\Application\\msedge.exe"),
            ]
        elif self.is_macos():
            # macOS Chrome paths
            possible_paths = [
                "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
                "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
            ]
        else:
            # Linux Chrome paths
            possible_paths = [
                "/usr/bin/google-chrome",
                "/usr/bin/google-chrome-stable",
                "/usr/bin/chromium-browser",
                "/usr/bin/microsoft-edge",
                "/opt/google/chrome/chrome",
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                logger.info(f"Found Chrome browser at: {path}")
                return path
        
        logger.warning("Chrome browser not found. Please ensure Chrome is installed.")
        return None

# Global platform utility instance
platform_utils = PlatformUtils()

def get_platform() -> str:
    """Get the current platform name"""
    return platform_utils.get_platform()

def is_windows() -> bool:
    """Check if running on Windows"""
    return platform_utils.is_windows()

def is_linux() -> bool:
    """Check if running on Linux"""
    return platform_utils.is_linux()

def is_macos() -> bool:
    """Check if running on macOS"""
    return platform_utils.is_macos()
