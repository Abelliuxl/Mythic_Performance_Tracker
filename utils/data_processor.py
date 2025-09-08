import pandas as pd
import re
from urllib.parse import quote
from config.settings import DUNGEON_NAME_MAP, DUNGEON_TIME_LIMIT, WCL_BASE_URL, WCL_ZONE_ID
from utils.logger import logger

class DataProcessor:
    @staticmethod
    def load_character_data(file_path):
        """加载角色数据"""
        try:
            char_df = pd.read_excel(file_path)
            logger.success(f"成功读取角色文件: {file_path}")
            return char_df
        except Exception as e:
            logger.error(f"无法读取角色文件 {file_path}: {e}")
            return None
    
    @staticmethod
    def build_wcl_url(server, character_name):
        """构建WCL URL"""
        return f"{WCL_BASE_URL}/character/cn/{quote(server.strip(), safe='')}/{quote(character_name.strip(), safe='')}?zone={WCL_ZONE_ID}"
    
    @staticmethod
    def parse_dungeon_data(row, dungeon_name_map=None):
        """解析副本数据行"""
        if dungeon_name_map is None:
            dungeon_name_map = DUNGEON_NAME_MAP
        
        try:
            a_tag = row.find("a", class_="Boss zone-boss-cell")
            if not a_tag:
                return None
            
            raw_dungeon = a_tag.text.strip()
            dungeon = dungeon_name_map.get(raw_dungeon, raw_dungeon)
            
            time_cells = row.find_all("td", class_="verbose main-table-number kills-cell")
            if len(time_cells) < 2:
                return None
            
            time_text = time_cells[1].get_text(strip=True)
            time_match = re.search(r"\d{1,2}:\d{2}", time_text)
            time_str = time_match.group(0) if time_match else "未知"
            level_match = re.search(r"\+(\d+)", time_text)
            plus_level = int(level_match.group(1)) if level_match else None
            
            # 计算是否限时
            t_split = time_str.split(":")
            run_seconds = int(t_split[0]) * 60 + int(t_split[1]) if len(t_split) == 2 else 9999
            limit = DUNGEON_TIME_LIMIT.get(dungeon)
            on_time = (limit is not None and run_seconds <= limit)
            result = "是" if on_time else "否"
            
            return {
                "副本": dungeon,
                "限时层数": plus_level,
                "通关时间": time_str,
                "是否限时": result
            }
        except Exception as e:
            logger.error(f"解析副本行失败: {e}")
            return None
    
    @staticmethod
    def format_display_level(row):
        """格式化显示层数"""
        lvl = row["限时层数"]
        if pd.isna(lvl):
            return "-"
        return f"+{int(lvl)}" if row["是否限时"] == "是" else f"+{int(lvl)}*"
    
    @staticmethod
    def create_pivot_table(df):
        """创建透视表"""
        pivot_df = df.pivot_table(
            index=["玩家", "角色名"],
            columns="副本",
            values="显示层数",
            aggfunc="first"
        ).fillna("-").reset_index()
        return pivot_df
    
    @staticmethod
    def validate_character_data(char_df):
        """验证角色数据格式"""
        required_columns = ["玩家", "角色名", "服务器", "职业"]
        missing_columns = [col for col in required_columns if col not in char_df.columns]
        
        if missing_columns:
            logger.error(f"角色数据缺少必要列: {missing_columns}")
            return False
        
        # 检查空值
        for col in required_columns:
            if char_df[col].isnull().any():
                logger.error(f"角色数据列 '{col}' 存在空值")
                return False
        
        logger.success("角色数据格式验证通过")
        return True
    
    @staticmethod
    def clean_character_name(name):
        """清理角色名"""
        return str(name).strip()
    
    @staticmethod
    def clean_server_name(server):
        """清理服务器名"""
        return str(server).strip()
    
    @staticmethod
    def get_character_class_map(char_df):
        """获取角色职业映射"""
        return dict(zip(char_df["角色名"], char_df["职业"]))
