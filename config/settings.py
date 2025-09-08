# 项目配置文件

# 副本映射与限时阈值（秒）
DUNGEON_NAME_MAP = {
    "Ara-Kara, City of Echoes": "艾拉-卡拉，回响之城",
    "Eco-Dome Al'dani": "奥尔达尼生态圆顶",
    "Halls of Atonement": "赎罪大厅",
    "Operation: Floodgate": "水闸行动",
    "Priory of the Sacred Flame": "圣焰隐修院",
    "Tazavesh: So'leah's Gambit": "塔扎维什: 索·莉亚的宏图",
    "Tazavesh: Streets of Wonder": "塔扎维什: 琳彩天街",
    "The Dawnbreaker": "破晨号",
}

DUNGEON_TIME_LIMIT = {
    "艾拉-卡拉，回响之城": 30 * 60,          # 30:00
    "奥尔达尼生态圆顶": 31 * 60,              # 31:00
    "赎罪大厅": 31 * 60,                     # 31:00
    "水闸行动": 33 * 60,                     # 33:00
    "圣焰隐修院": 32 * 60 + 30,              # 32:30
    "塔扎维什: 索·莉亚的宏图": 30 * 60,        # 30:00
    "塔扎维什: 琳彩天街": 35 * 60,             # 35:00
    "破晨号": 31 * 60,                      # 31:00
}

# 职业颜色映射
CLASS_COLOR_MAP = {
    "死亡骑士": "C41F3B", "恶魔猎手": "A330C9", "德鲁伊": "FF7D0A", "猎人": "ABD473",
    "法师": "69CCF0", "武僧": "00FF96", "圣骑士": "F58CBA", "骑士": "F58CBA",
    "牧师": "FFFFFF", "潜行者": "FFF569", "盗贼": "FFF569", "萨满": "0070DE",
    "术士": "9482C9", "战士": "C79C6E"
}

# 层数颜色映射（彩虹风格渐变色）
LAYER_COLOR_MAP = {
    2:  "E3F2FD",  3:  "BBDEFB",  4:  "81D4FA",  5:  "4DD0E1",
    6:  "4DB6AC",  7:  "81C784",  8:  "AED581",  9:  "DCE775",
    10: "FFF176", 11: "FFD54F", 12: "FFB74D", 13: "FF8A65",
    14: "F48FB1", 15: "F06292", 16: "EC407A", 17: "E91E63",
    18: "F44336", 19: "D32F2F",
}

# 浏览器配置
BROWSER_CONFIG = {
    "headless": True,
    "disable_gpu": True,
    "no_sandbox": True,
    "log_level": "3",
    "proxy_server": "http://192.168.5.101:7890",
    "page_load_strategy": "none",
    "chromedriver_path": None  # 现在由平台工具自动检测，无需手动配置
}

# 爬虫配置
CRAWLER_CONFIG = {
    "max_attempts": 3,
    "wait_time": 6,
    "timeout": 10
}

# 文件路径配置
FILE_PATHS = {
    "character_info": "data/character_info.xlsx",
    "result": "data/result.xlsx",
    "log_file": "logs/crawl_log.txt"
}

# WCL URL配置
WCL_BASE_URL = "https://www.warcraftlogs.com"
WCL_ZONE_ID = "45"  # 赛季区域ID，需要手动更新
