# 项目配置文件

# 副本映射与限时阈值（秒）
# 从 Blizzard 国服页面获取的副本名为中文，直接使用中文名
DUNGEON_NAME_MAP = {}

# 副本限时阈值（秒）— "至暗之夜"第1赛季
DUNGEON_TIME_LIMIT = {
    "迈萨拉洞窟": 33 * 60 + 30,      # 33:30
    "通天峰": 33 * 60,               # 33:00
    "艾杰斯亚学院": 30 * 60,          # 30:00
    "萨隆矿坑": 32 * 60,             # 32:00
    "风行者之塔": 33 * 60,           # 33:00
    "魔导师平台": 31 * 60,           # 31:00
    "执政团之座": 34 * 60,           # 34:00
    "节点希纳斯": 33 * 60,           # 33:00
}

# 副本简称映射
DUNGEON_SHORT_NAME_MAP = {
    "迈萨拉洞窟": "洞窟",
    "通天峰": "通天",
    "艾杰斯亚学院": "学院",
    "萨隆矿坑": "矿坑",
    "风行者之塔": "风塔",
    "魔导师平台": "魔导",
    "执政团之座": "执政",
    "节点希纳斯": "节点",
}

# 副本颜色映射
DUNGEON_COLOR_MAP = {
    "迈萨拉洞窟": "rgba(255, 99, 132, 0.8)",
    "通天峰": "rgba(54, 162, 235, 0.8)",
    "艾杰斯亚学院": "rgba(255, 206, 86, 0.8)",
    "萨隆矿坑": "rgba(75, 192, 192, 0.8)",
    "风行者之塔": "rgba(153, 102, 255, 0.8)",
    "魔导师平台": "rgba(255, 159, 64, 0.8)",
    "执政团之座": "rgba(199, 199, 199, 0.8)",
    "节点希纳斯": "rgba(83, 102, 255, 0.8)",
}

# 职业颜色映射
CLASS_COLOR_MAP = {
    "死亡骑士": "C41F3B", "恶魔猎手": "A330C9", "德鲁伊": "FF7D0A", "猎人": "ABD473",
    "法师": "69CCF0", "武僧": "00FF96", "圣骑士": "F58CBA",
    "牧师": "FFFFFF", "盗贼": "FFF569", "萨满": "0070DE",
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
    "proxy_server": "http://127.0.0.1:7890",
    "page_load_strategy": "eager",
    "chromedriver_path": None,
    # Linux headless 必要选项
    "disable_dev_shm_usage": True,
    "disable_setuid_sandbox": True,
    # 额外的Chrome选项
    "window_size": "1920,1080",
    "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "disable_web_security": False,
    "ignore_certificate_errors": False,
    "disable_extensions": True,
    "disable_plugins": True,
    "disable_images": False,
    "disable_javascript": False,
    "blink_settings": {"imagesEnabled": True}
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
    "log_file": "logs/process_record.txt"
}

# WCL URL配置（已归档到 legacy/）
WCL_BASE_URL = "https://www.warcraftlogs.com"
WCL_ZONE_ID = "45"  # 赛季区域ID，需要手动更新

# Blizzard 国服角色页面配置
BLIZZARD_BASE_URL = "https://wow.blizzard.cn/character/"
BLIZZARD_API_BASE = "https://webapi.blizzard.cn/wow-armory-server/api"

# 服务器中文名 → 英文 slug 映射
SERVER_SLUG_MAP = {
    "回音山": "echo-ridge", "霜之哀伤": "frostmourne", "死亡之翼": "deathwing",
    "通灵学院": "scholomance", "斯坦索姆": "stratholme", "影之哀伤": "shadowmourne",
    "米奈希尔": "menethil",     "伊森利恩": "isillien", "图拉扬": "turalyon",
    "诺兹多姆": "nozdormu", "神圣之歌": "holy-chanter",
    "丽丽（四川）": "li-li", "阿古斯": "argus", "阿卡玛": "akama",
    "阿拉索": "arathor", "阿曼尼": "amani", "阿纳克洛斯": "anachronos",
    "阿努巴拉克": "anubarak", "埃德萨拉": "azshara", "埃加洛尔": "aggramar",
    "埃雷达尔": "eredar", "埃苏雷格": "azuregos", "艾露恩": "elune",
    "艾莫莉丝": "emeralds", "艾萨拉": "azshara", "安多哈尔": "andorhal",
    "安戈拉": "ungoro", "安格博达": "angrboda", "安纳塞隆": "anetheron",
    "安其拉": "ahnqiraj", "安苏": "ansu", "暗影迷宫": "shadowlabyrinth",
    "暗影议会": "shadowmoon", "奥达曼": "uldaman", "奥尔加隆": "algolon",
    "奥蕾莉亚": "alleria", "奥斯里安": "ossirian", "奥妮克希亚": "onyxia",
    "巴瑟拉斯": "barthilas", "巴纳扎尔": "balnazzar", "白骨荒野": "bonewaste",
    "白银之手": "lordaeron", "暴风祭坛": "altars", "冰风岗": "chillwind",
    "冰霜之刃": "frostblade", "布莱克摩": "blackmoore", "布鲁塔卢斯": "brutallus",
    "壁炉谷": "hearthglen", "裁决之地": "judgement", "尘风峡谷": "dustwind",
    "晨星之灵": "morningstar", "雏龙之翼": "whelps", "刺骨利刃": "bonedagger",
    "达尔坎": "darkhan", "达克萨隆": "drakthul", "达拉然": "dalaran",
    "达隆米尔": "darrowmere", "大地之怒": "rage", "大漩涡": "maelstrom",
    "戴索姆": "dathomir", "丹莫德": "dunmorogh", "德拉诺": "draenor",
    "迪瑟洛克": "detheroc", "地狱咆哮": "hellscream", "地狱之石": "hellstone",
    "杜隆坦": "durotan", "死亡熔炉": "deathforge", "末日行者": "doomwalker",
    "多米尼奥": "dominion", "厄祖玛特": "ozumat", "恶魔之翼": "demonwing",
    "恶魔之魂": "demonsoul", "耳语海岸": "whispercoast", "范达姆": "vandam",
    "范克里夫": "vancleef", "菲拉斯": "feralas", "翡翠梦境": "emeralddream",
    "芬里斯": "fenris", "风暴裂隙": "stormrift", "风暴之怒": "stormrage",
    "风暴之眼": "stormeye", "风行者": "windrunner", "弗塞雷克": "forserek",
    "弗斯塔德": "falstad", "斧王之刃": "axeblade", "符文图腾": "runetotem",
    "凤凰之神": "alar", "盖斯": "gyth", "戈古纳斯": "gorgonnash",
    "戈提克": "gothik", "格雷迈恩": "greymane", "格瑞姆巴托": "grimbatol",
    "古尔丹": "guldan", "古拉巴什": "gurubashi", "冠军之刃": "championblade",
    "光明使者": "lightbringer", "鬼雾峰": "dreadmist", "国王之谷": "kingsvalley",
    "哈卡": "hakkar", "哈兰": "halaa", "海克泰尔": "hektait",
    "海加尔": "hyjal", "寒冰皇冠": "icecrown", "嚎风峡湾": "howlingfjord",
    "黑暗虚空": "darkvoid", "黑暗之矛": "darkspear", "黑暗之门": "darkportal",
    "黑锋哨站": "ebonhold", "黑龙军团": "blackdragon", "黑铁": "blackiron",
    "黑翼之巢": "blackwinglair", "红龙军团": "reddragon", "红云台地": "redcloud",
    "红玉圣殿": "rubysanctum", "火焰之树": "firetree", "激流堡": "arathi",
    "吉安娜": "jaina", "吉卡洛斯": "jikarlos", "加德纳尔": "gardner",
    "加尔": "gar", "加基森": "gadgetzan", "加里索斯": "garithos",
    "加兹鲁维": "gazlowe", "金度": "jindo", "金色平原": "goldenplains",
    "荆棘谷": "stranglethorn", "巨龙之吼": "dragonroar", "军团之心": "legionheart",
    "卡德加": "khadgar", "卡拉赞": "karazhan", "卡利姆多": "kalimdor",
    "卡珊德拉": "cassandra", "凯尔萨斯": "kaelthas", "凯恩血蹄": "cairne",
    "坎雷德": "kanrethad", "克尔苏加德": "kelthuzad", "克拉苏斯": "krasus",
    "克洛玛古斯": "chromaggus", "克苏恩": "cthun", "恐怖图腾": "grimtotem",
    "库尔提拉斯": "kultiras", "库卡隆": "korkron", "奎尔丹纳斯": "queldanas",
    "奎尔萨拉斯": "quelthalas", "拉格纳罗斯": "ragnaros", "拉贾克斯": "rajaxx",
    "拉文凯斯": "ravencrest", "拉文霍德": "ravenholdt", "莱索恩": "lethon",
    "兰娜瑟尔": "lanathel", "蓝龙军团": "bluedragon", "雷霆号角": "thunderhorn",
    "雷霆之王": "thunderking", "雷克萨": "rexxar", "雷斧堡垒": "thunderaxe",
    "莉亚德琳": "liadrin", "烈焰荆棘": "firethorn", "龙骨平原": "dragonbone",
    "龙喉": "dragonmaw", "龙牙之刃": "fang", "卢森塔尔": "lusenthrall",
    "罗曼斯": "rommath", "洛丹伦": "lordaeron", "洛萨": "lothar",
    "玛法里奥": "malfurion", "玛格曼达": "magmadar", "玛克扎尔": "malchezaar",
    "玛拉顿": "maraudon", "玛里苟斯": "malygos", "玛洛加尔": "marrowgar",
    "玛诺洛斯": "mannoroth", "玛瑟里顿": "magtheridon", "麦迪文": "medivh",
    "蛮锤": "wildhammer", "梦境林地": "dreamwood", "密林游侠": "ranger",
    "摩摩尔": "murmur", "莫德雷萨": "mordresh", "莫格莱尼": "mograine",
    "穆戈尔": "muggle", "暮色森林": "duskwood", "末日祷告": "doomsayer",
    "纳克萨玛斯": "naxxramas", "纳沙塔尔": "nazjatar", "奈法利安": "nefarian",
    "奈萨里奥": "neltharion", "耐奥祖": "nerzhul", "耐克鲁斯": "nefarius",
    "诺莫瑞根": "gnomeregan", "诺森德": "northrend", "潘达利亚": "pandaria",
    "破碎大厅": "shatteredhalls", "破碎岭": "shatteredridge",
    "普瑞斯托": "prestor", "破碎群岛": "brokenisles",
    "千针石林": "thousandneedles", "轻风之语": "whisperwind",
    "青铜龙军团": "bronzedragon", "燃烧军团": "burninglegion",
    "燃烧平原": "burningplains", "起源之门": "gateway",
    "瑞文戴尔": "rivendare", "萨尔": "thrall", "萨菲隆": "sapphiron",
    "萨格拉斯": "sargeras", "萨塔里奥": "sartarion", "沙塔斯": "shattrath",
    "塞拉摩": "theramore", "塞拉赞恩": "therazane", "塞纳留斯": "cenarius",
    "塞泰克": "sethekk", "桑德兰": "thunderaan", "沙怒": "sandfury",
    "山丘之王": "mountainking", "闪电之刃": "lightningblade",
    "审判之锤": "judgementhammer", "深渊之巢": "deepnest",
    "深渊之喉": "abyssthroat", "深渊领主": "abyssallord",
    "生态船": "ecodome", "圣光守护": "lightguard", "世界之树": "worldtree",
    "霜狼": "frostwolf", "水晶之刺": "crystalspine",
    "斯克提斯": "skettis", "死亡之门": "deathgate", "四风谷": "valleyfourwinds",
    "苏拉玛": "suramar", "索拉丁": "thoradin", "索瑞森": "thaurissan",
    "索塔纳索尔": "sothanasor", "神圣之地": "sacredland",
    "塔迪乌斯": "thaddius", "塔拉多": "talador", "塔兰吉": "talanji",
    "塔伦米尔": "tarrenmill", "泰兰德": "tyrande", "泰拉尔": "taerar",
    "提尔之手": "tyrshand", "提瑞斯法": "tirisfal", "天空之墙": "skywall",
    "甜水绿洲": "sweetoasis", "屠魔山谷": "demonvalley",
    "托尔巴拉德": "tolbarad", "托塞德林": "tortheldrin",
    "瓦拉斯塔兹": "vaelastrasz", "瓦里安": "varian", "瓦丝琪": "vashj",
    "外域": "outland", "万神殿": "pantheon", "亡语者": "deathsayer",
    "维克尼拉斯": "veknilash", "维克洛尔": "veklor", "维纶": "velen",
    "温蕾萨": "vereesa", "沃金": "voljin", "巫妖之王": "lichking",
    "无尽之海": "endlesssea", "乌苏雷": "uthok", "午夜之镰": "midnightsickle",
    "希尔盖": "heigan", "希尔瓦娜斯": "sylvanas", "鲜血熔炉": "bloodfurnace",
    "邪能之心": "felheart", "邪能之颅": "felskull", "辛达苟萨": "sindragosa",
    "熊猫酒仙": "brewmaster", "血色十字军": "scarletcrusade",
    "血蹄": "bloodhoof", "血牙": "bloodfang", "血与荣耀": "bloodglory",
    "血咒之地": "bloodcurse", "迅捷微风": "swiftwind", "鸦羽山": "ravenmountain",
    "雅立史卓莎": "alexstrasza", "亚雷戈斯": "arygos", "炎刃": "fireblade",
    "伊兰尼库斯": "eranikus", "伊利丹": "illidan", "伊莫塔尔": "immolthar",
    "伊瑟拉": "ysera", "伊森德雷": "ysondre", "伊萨里奥斯": "isarios",
    "遗忘海岸": "forgottencoast", "鹰巢山": "aeriepeak",
    "永恒之井": "wellofeternity", "永夜港": "eternals", "幽暗城": "undercity",
    "幽魂之地": "ghostlands", "影歌": "shadowsong", "影牙要塞": "shadowfang",
    "羽月": "feathermoon", "元素裂口": "elementalrift",
    "月光林地": "moonglade", "月亮石": "moonstone", "月神殿": "templemoon",
    "扎拉赞恩": "zalazane", "斩魔者": "demonslayer", "战歌": "warsong",
    "蜘蛛王国": "spiderrealm", "主宰之剑": "dominatorsword",
    "铸龙": "dragonforge", "灼热峡谷": "burninggorge", "兹格雷尔": "zulgurub",
}

# Cookie/Session 持久化配置
SESSION_CONFIG = {
    "user_data_dir": "chrome_profile",  # Chrome 用户数据目录
    "first_run_message": "首次使用需要登录战网。请在有显示器的电脑上运行 login_helper.py"
}

# HTML报告文件管理配置
REPORT_CONFIG = {
    "output_dir": "reports",
    "max_files": 20,  # 最大保留文件数量
    "compress_old_files": True,  # 是否压缩旧文件
    "compress_after_days": 7,  # 多少天后压缩
    "delete_after_days": 30,  # 多少天后删除（0表示不删除）
    "organize_by_date": True,  # 按日期组织文件
    "keep_latest_copy": True,  # 保留最新版本副本
    "latest_filename": "mythic_performance_report_latest.html"
}
