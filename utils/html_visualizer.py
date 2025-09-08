import pandas as pd
import numpy as np
import json
from datetime import datetime
import traceback
from openpyxl import load_workbook
from config.settings import CLASS_COLOR_MAP, LAYER_COLOR_MAP, DUNGEON_NAME_MAP, DUNGEON_TIME_LIMIT
from utils.logger import logger

class HTMLVisualizer:
    def __init__(self):
        self.template = self._get_html_template()
    
    def generate_html_report(self, character_info_path, result_path, output_path):
        """生成HTML可视化报告"""
        try:
            # 读取数据（带兜底）
            char_df = self._safe_read_excel(character_info_path)
            result_df = self._safe_read_excel(result_path, preferred_sheet="明细")

            # 再次整体清洗，确保无数组/列表残留
            char_df = self._sanitize_dataframe(char_df)
            result_df = self._sanitize_dataframe(result_df)

            # 标准化列名：确保存在关键列
            expected_cols = {"玩家", "角色名", "服务器", "副本", "通关时间", "限时层数", "是否限时"}
            missing_cols = [c for c in ["玩家", "角色名", "副本"] if c not in result_df.columns]
            if missing_cols:
                raise ValueError(f"结果表缺少必要列: {missing_cols}")

            # 数值与标志列标准化
            result_df["限时层数"] = pd.to_numeric(result_df.get("限时层数"), errors="coerce")
            result_df["是否限时"] = result_df.get("是否限时").astype(str).str.strip()

            # 无条件重建“显示层数”列，避免原文件中携带的异常类型
            def _fmt(row):
                lvl = row.get("限时层数")
                if pd.isna(lvl):
                    return "-"
                try:
                    lvl_i = int(float(lvl))
                except Exception:
                    return "-"
                return f"+{lvl_i}" if row.get("是否限时") == "是" else f"+{lvl_i}*"
            result_df["显示层数"] = result_df.apply(_fmt, axis=1)

            # 再次清洗
            result_df = self._sanitize_dataframe(result_df)
            
            # 生成HTML
            html_content = self._generate_html_content(char_df, result_df)
            
            # 保存文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.success(f"HTML可视化报告已生成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"生成HTML报告失败: {e}\n{traceback.format_exc()}")
            return False

    def _safe_read_excel(self, file_path, preferred_sheet=None):
        """安全读取Excel：先尝试pandas，失败则退化到openpyxl逐行读取。"""
        # 优先尝试 pandas（默认参数）
        try:
            if preferred_sheet is not None:
                df = pd.read_excel(file_path, sheet_name=preferred_sheet)
            else:
                df = pd.read_excel(file_path)
            logger.info(f"读取Excel(pandas)成功: {file_path}{' / ' + preferred_sheet if preferred_sheet else ''}")
            return self._sanitize_dataframe(df)
        except Exception as e1:
            logger.warning(f"pandas读取失败，改用engine=openpyxl重试: {e1}")
            # 明确指定engine重试
            try:
                if preferred_sheet is not None:
                    df = pd.read_excel(file_path, sheet_name=preferred_sheet, engine="openpyxl")
                else:
                    df = pd.read_excel(file_path, engine="openpyxl")
                logger.info(f"读取Excel(pandas+openpyxl)成功: {file_path}{' / ' + preferred_sheet if preferred_sheet else ''}")
                return self._sanitize_dataframe(df)
            except Exception as e2:
                logger.warning(f"pandas+openpyxl仍失败，降级openpyxl逐行读取: {e2}")
                # 使用 openpyxl 读取
                wb = load_workbook(filename=file_path, data_only=True, read_only=True)
                sheet = None
                if preferred_sheet and preferred_sheet in wb.sheetnames:
                    sheet = wb[preferred_sheet]
                else:
                    sheet = wb[wb.sheetnames[0]]

                # 读取所有行并标准化
                raw_rows = [list(r) for r in sheet.iter_rows(values_only=True)]
                if not raw_rows:
                    return pd.DataFrame()
                max_len = max(len(r) for r in raw_rows)

                def sanitize_header(val, idx):
                    if isinstance(val, (str, int, float, bool)):
                        s = str(val).strip()
                    else:
                        s = ""
                    if not s or s.lower() == 'none' or s.lower() == 'nan':
                        s = f"列{idx+1}"
                    return s

                headers = [sanitize_header(raw_rows[0][i] if i < len(raw_rows[0]) else None, i) for i in range(max_len)]
                # 去重列名
                seen = {}
                for i, name in enumerate(headers):
                    if name in seen:
                        seen[name] += 1
                        headers[i] = f"{name}_{seen[name]}"
                    else:
                        seen[name] = 1

                def coerce_scalar(v):
                    try:
                        if isinstance(v, np.ndarray):
                            return v.flatten()[0] if v.size > 0 else None
                        if isinstance(v, (list, tuple)):
                            return v[0] if len(v) > 0 else None
                        return v
                    except Exception:
                        return v

                data_dicts = []
                for r in raw_rows[1:]:
                    row_dict = {
                        headers[i]: coerce_scalar(r[i] if i < len(r) else None)
                        for i in range(max_len)
                    }
                    data_dicts.append(row_dict)

                df = pd.DataFrame(data_dicts)
                logger.info(f"读取Excel(openpyxl)成功: {file_path} / {sheet.title}")
                return self._sanitize_dataframe(df)

    def _sanitize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """将DataFrame中可能的ndarray/列表等非常规单元值压平为标量。"""
        def coerce_scalar(v):
            try:
                if isinstance(v, np.ndarray):
                    return v.flatten()[0] if v.size > 0 else None
                if isinstance(v, (list, tuple)):
                    return v[0] if len(v) > 0 else None
                return v
            except Exception:
                return v

        return df.map(coerce_scalar)
    
    def _generate_html_content(self, char_df, result_df):
        """生成HTML内容"""
        # 准备数据
        summary_data = self._prepare_summary_data(result_df)
        character_stats = self._prepare_character_stats(char_df, result_df)
        dungeon_stats = self._prepare_dungeon_stats(result_df)
        
        # 生成图表数据
        charts_json = self._prepare_charts_data(result_df, summary_data, char_df)

        # 顶部KPI卡片
        kpi_html = self._generate_kpi_cards(result_df)
        
        # 填充模板
        html_content = self.template.replace("{{TITLE}}", "Mythic+ 性能追踪报告")
        html_content = html_content.replace("{{GENERATION_TIME}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        html_content = html_content.replace("{{KPI_CARDS}}", kpi_html)
        html_content = html_content.replace("{{SUMMARY_TABLE}}", self._generate_summary_table(summary_data))
        html_content = html_content.replace("{{CHARACTER_STATS}}", self._generate_character_stats(character_stats))
        html_content = html_content.replace("{{DUNGEON_STATS}}", self._generate_dungeon_stats(dungeon_stats))
        html_content = html_content.replace("{{CHARTS_DATA}}", json.dumps(charts_json, ensure_ascii=False))
        
        return html_content
    
    def _prepare_summary_data(self, result_df):
        """准备总览数据（避开pandas透视，提升鲁棒性）"""
        try:
            for col in ["玩家", "角色名", "副本", "显示层数"]:
                if col in result_df.columns:
                    result_df[col] = result_df[col].astype(str)

            matrix = {}
            for _, r in result_df.iterrows():
                player = r.get("玩家")
                char = r.get("角色名")
                dungeon = r.get("副本")
                disp = r.get("显示层数", "-")
                if pd.isna(player) or pd.isna(char) or pd.isna(dungeon):
                    continue
                key = (str(player), str(char))
                if key not in matrix:
                    matrix[key] = {}
                matrix[key].setdefault(str(dungeon), str(disp))

            summary_data = []
            for (player, char), dun_map in matrix.items():
                summary_data.append({
                    "player": player,
                    "character": char,
                    "dungeons": dun_map
                })
            return summary_data
        except Exception:
            logger.error("构建总览数据失败:\n" + traceback.format_exc())
            return []
    
    def _prepare_character_stats(self, char_df, result_df):
        """准备角色统计数据"""
        stats = []
        for _, char in char_df.iterrows():
            char_data = result_df[result_df["角色名"] == char["角色名"]]
            if not char_data.empty:
                avg_level = char_data["限时层数"].mean()
                timed_runs = len(char_data[char_data["是否限时"] == "是"])
                total_runs = len(char_data)
                
                stats.append({
                    "player": char["玩家"],
                    "character": char["角色名"],
                    "server": char["服务器"],
                    "class": char["职业"],
                    "avg_level": round(avg_level, 1),
                    "timed_runs": timed_runs,
                    "total_runs": total_runs,
                    "timed_rate": round((timed_runs / total_runs * 100), 1) if total_runs > 0 else 0
                })
        
        return stats
    
    def _prepare_dungeon_stats(self, result_df):
        """准备副本统计数据"""
        stats = []
        for dungeon in result_df["副本"].unique():
            dungeon_data = result_df[result_df["副本"] == dungeon]
            avg_time = self._time_to_seconds(dungeon_data["通关时间"]).mean()
            avg_level = dungeon_data["限时层数"].mean()
            timed_runs = len(dungeon_data[dungeon_data["是否限时"] == "是"])
            total_runs = len(dungeon_data)
            
            stats.append({
                "dungeon": dungeon,
                "avg_time": self._seconds_to_time_format(avg_time),
                "avg_level": round(avg_level, 1),
                "timed_runs": timed_runs,
                "total_runs": total_runs,
                "timed_rate": round((timed_runs / total_runs * 100), 1) if total_runs > 0 else 0
            })
        
        return stats
    
    def _prepare_charts_data(self, result_df, summary_data, char_df):
        """准备图表数据"""
        charts = {
            "level_distribution": {},
            "class_performance": {},
            "dungeon_performance": {}
        }
        
        # 等级分布（只统计有效数值）
        levels_series = pd.to_numeric(result_df["限时层数"], errors="coerce").dropna()
        level_counts = levels_series.value_counts().sort_index()
        charts["level_distribution"] = {
            "labels": [f"+{int(l)}" for l in level_counts.index.tolist()],
            "data": [int(x) for x in level_counts.values.tolist()]
        }
        
        # 职业表现（按职业聚合）
        char_to_class = dict(zip(char_df["角色名"], char_df["职业"]))
        class_levels = {}
        for _, row in result_df.iterrows():
            cls = char_to_class.get(row["角色名"], "未知职业")
            lvl = row["限时层数"]
            if pd.notna(lvl):
                class_levels.setdefault(cls, []).append(float(lvl))

        for cls, levels in class_levels.items():
            charts["class_performance"][cls] = {
                "avg_level": round(sum(levels) / len(levels), 1),
                "count": len(levels),
                "color": f"#{CLASS_COLOR_MAP.get(cls, '888888')}"
            }
        
        # 副本表现
        for dungeon in result_df["副本"].dropna().unique():
            dungeon_data = result_df[result_df["副本"] == dungeon]
            avg_lvl = pd.to_numeric(dungeon_data["限时层数"], errors="coerce").mean()
            timed_rate = 0
            if len(dungeon_data) > 0:
                timed_rate = round((dungeon_data["是否限时"].astype(str).str.strip() == "是").sum() / len(dungeon_data) * 100, 1)
            charts["dungeon_performance"][str(dungeon)] = {
                "avg_level": round(avg_lvl, 1) if pd.notna(avg_lvl) else 0,
                "timed_rate": timed_rate
            }
        
        return charts

    def _generate_kpi_cards(self, result_df):
        """生成顶部关键指标KPI卡片"""
        total_runs = len(result_df)
        total_chars = result_df["角色名"].nunique() if not result_df.empty else 0
        timed_runs = (result_df["是否限时"] == "是").sum() if "是否限时" in result_df.columns else 0
        timed_rate = round((timed_runs / total_runs * 100), 1) if total_runs > 0 else 0
        avg_level = round(pd.to_numeric(result_df["限时层数"], errors='coerce').mean(), 1) if not result_df.empty else 0

        return f"""
        <div class=\"kpi-grid\">
            <div class=\"kpi-card\">
                <div class=\"kpi-label\">总运行数</div>
                <div class=\"kpi-value\">{total_runs}</div>
            </div>
            <div class=\"kpi-card\">
                <div class=\"kpi-label\">角色数量</div>
                <div class=\"kpi-value\">{total_chars}</div>
            </div>
            <div class=\"kpi-card\">
                <div class=\"kpi-label\">限时率</div>
                <div class=\"kpi-value\">{timed_rate}%</div>
            </div>
            <div class=\"kpi-card\">
                <div class=\"kpi-label\">平均层数</div>
                <div class=\"kpi-value\">{avg_level}</div>
            </div>
        </div>
        """
    
    def _generate_summary_table(self, summary_data):
        """生成总览表格HTML（搜索 + 冻结前两列 + 可排序）"""
        html = """
        <div class=\"table-container\">
            <div class=\"table-toolbar\">
                <h3>限时总览</h3>
                <div class=\"toolbar-actions\">
                    <input id=\"summarySearch\" class=\"search-input\" type=\"search\" placeholder=\"搜索玩家/角色/副本...\" />
                    <button id=\"clearSearch\" class=\"btn\">清除</button>
                </div>
            </div>
            <div class=\"table-wrapper\">
                <table id=\"summaryTable\" class=\"summary-table\">
                    <thead>
                        <tr>
                            <th class=\"sticky-col sticky-col-1 sortable\" data-type=\"text\">玩家</th>
                            <th class=\"sticky-col sticky-col-2 sortable\" data-type=\"text\">角色名</th>
        """
        
        # 添加副本列头（先按配置顺序，再追加未配置副本；使用全量union）
        dungeons = []
        if summary_data:
            seen = set()
            union = []
            for item in summary_data:
                for d in item.get("dungeons", {}).keys():
                    if d not in seen:
                        seen.add(d)
                        union.append(d)
            preferred = list(DUNGEON_TIME_LIMIT.keys())
            dungeons = [d for d in preferred if d in seen] + [d for d in union if d not in preferred]
            for dungeon in dungeons:
                html += f'<th class="sortable" data-type="level">{dungeon}</th>'
        
        html += """
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # 添加数据行
        for player_data in summary_data:
            html += f"""
                        <tr>
                            <td class="sticky-col sticky-col-1">{player_data["player"]}</td>
                            <td class="sticky-col sticky-col-2">{player_data["character"]}</td>
            """
            for dungeon in dungeons:
                level = player_data["dungeons"].get(dungeon, "-")
                level_class = self._get_level_class(level)
                html += f'<td class="{level_class}">{level}</td>'
            html += "</tr>"
        
        html += """
                    </tbody>
                </table>
            </div>
        </div>
        """
        
        return html
    
    def _generate_character_stats(self, character_stats):
        """生成角色统计HTML"""
        html = """
        <div class="stats-grid">
            <h3>角色统计</h3>
            <div class="stats-cards">
        """
        
        for stat in character_stats:
            class_color = CLASS_COLOR_MAP.get(stat["class"], "FFFFFF")
            html += f"""
                <div class="stat-card">
                    <div class="card-header" style="border-left-color: #{class_color};">
                        <div class="character-info">
                            <div class="character-name">{stat["character"]}</div>
                            <div class="character-server">{stat["server"]}</div>
                        </div>
                        <div class="character-class" style="color: #{class_color};">{stat["class"]}</div>
                    </div>
                    <div class="card-content">
                        <div class="stat-item">
                            <span class="stat-label">平均等级</span>
                            <span class="stat-value">{stat["avg_level"]}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">限时完成</span>
                            <span class="stat-value">{stat["timed_runs"]}/{stat["total_runs"]}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">限时率</span>
                            <span class="stat-value">{stat["timed_rate"]}%</span>
                        </div>
                    </div>
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def _generate_dungeon_stats(self, dungeon_stats):
        """生成副本统计HTML"""
        html = """
        <div class="stats-grid">
            <h3>副本统计</h3>
            <div class="stats-cards">
        """
        
        for stat in dungeon_stats:
            html += f"""
                <div class="stat-card">
                    <div class="card-header">
                        <div class="dungeon-name">{stat["dungeon"]}</div>
                    </div>
                    <div class="card-content">
                        <div class="stat-item">
                            <span class="stat-label">平均等级</span>
                            <span class="stat-value">{stat["avg_level"]}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">平均时间</span>
                            <span class="stat-value">{stat["avg_time"]}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">限时率</span>
                            <span class="stat-value">{stat["timed_rate"]}%</span>
                        </div>
                    </div>
                </div>
            """
        
        html += """
            </div>
        </div>
        """
        
        return html
    
    def _get_level_class(self, level):
        """获取等级样式类"""
        if level == "-":
            return "level-empty"
        try:
            level_num = int(level.replace("+", "").replace("*", ""))
            return f"level-{level_num}"
        except:
            return "level-empty"
    
    def _time_to_seconds(self, time_series):
        """将时间字符串转换为秒数"""
        seconds = []
        for time_str in time_series:
            try:
                parts = time_str.split(":")
                seconds.append(int(parts[0]) * 60 + int(parts[1]))
            except:
                seconds.append(0)
        return pd.Series(seconds)
    
    def _seconds_to_time_format(self, seconds):
        """将秒数转换为时间格式"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def _get_html_template(self):
        """获取HTML模板"""
        return """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{TITLE}}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
            line-height: 1.6;
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            text-align: center;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        .header h1 {
            font-size: 2.5em;
            color: #2c3e50;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #667eea, #764ba2);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .header p {
            color: #7f8c8d;
            font-size: 1.1em;
        }

        .section {
            background: rgba(255, 255, 255, 0.95);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        }

        .section h3 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.8em;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
        }

        .table-container {
            overflow-x: auto;
        }

        .table-wrapper {
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .summary-table {
            width: 100%;
            border-collapse: collapse;
            background: white;
        }

        .summary-table th,
        .summary-table td {
            padding: 15px 12px;
            text-align: center;
            border: 1px solid #e0e0e0;
            font-weight: 500;
        }

        .summary-table th {
            background: linear-gradient(45deg, #667eea, #764ba2);
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            position: sticky;
            top: 0;
            z-index: 1;
        }

        .summary-table tr:nth-child(even) {
            background-color: #f8f9fa;
        }

        .summary-table tr:hover {
            background-color: #e3f2fd;
            transition: background-color 0.3s ease;
        }

        /* 等级颜色样式 */
        .level-empty {
            background-color: #DDDDDD !important;
            color: #4b5563;
        }

        """ + "\n".join([f"""
        .level-{level} {{
            background-color: #{color} !important;
            color: #1f2937;
            font-weight: bold;
        }}
        """ for level, color in LAYER_COLOR_MAP.items()]) + """

        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
        }

        .stats-cards {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
        }

        .stat-card {
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
        }

        .card-header {
            padding: 20px;
            border-left: 5px solid #667eea;
            border-bottom: 1px solid #e0e0e0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .character-info {
            flex: 1;
        }

        .character-name {
            font-size: 1.2em;
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 5px;
        }

        .character-server {
            color: #7f8c8d;
            font-size: 0.9em;
        }

        .character-class {
            font-weight: 600;
            font-size: 1.1em;
        }

        .dungeon-name {
            font-size: 1.2em;
            font-weight: 600;
            color: #2c3e50;
        }

        .card-content {
            padding: 20px;
        }

        .stat-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
            padding: 8px 0;
            border-bottom: 1px solid #f0f0f0;
        }

        .stat-item:last-child {
            border-bottom: none;
            margin-bottom: 0;
        }

        .stat-label {
            color: #7f8c8d;
            font-weight: 500;
        }

        .stat-value {
            font-weight: 600;
            color: #2c3e50;
            font-size: 1.1em;
        }

        .charts-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 30px;
            margin-top: 30px;
        }

        .chart-card {
            background: white;
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
        }

        .chart-card h4 {
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.3em;
            text-align: center;
        }

        .chart-container {
            position: relative;
            height: 300px;
        }

        .footer {
            text-align: center;
            padding: 20px;
            color: rgba(255, 255, 255, 0.8);
            font-size: 0.9em;
        }

        @media (max-width: 768px) {
            .container {
                padding: 10px;
            }
            
            .header h1 {
                font-size: 2em;
            }
            
            .stats-cards {
                grid-template-columns: 1fr;
            }
            
            .charts-container {
                grid-template-columns: 1fr;
            }
            
            .summary-table th,
            .summary-table td {
                padding: 8px 6px;
                font-size: 0.9em;
            }
        }

        /* KPI Cards */
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }
        .kpi-card {
            background: white;
            border-radius: 12px;
            padding: 16px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.08);
            text-align: center;
        }
        .kpi-label {
            color: #6b7280;
            font-size: 0.9em;
        }
        .kpi-value {
            color: #111827;
            font-size: 1.6em;
            font-weight: 700;
            margin-top: 6px;
        }

        /* 新增：工具栏与按钮样式 */
        .header-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 6px;
        }
        .header-actions { display: flex; gap: 8px; }
        .btn {
            background: #eef2ff;
            color: #374151;
            border: 1px solid #e5e7eb;
            padding: 8px 12px;
            border-radius: 10px;
            cursor: pointer;
            transition: .2s ease;
        }
        .btn:hover { transform: translateY(-1px); box-shadow: 0 8px 16px rgba(0,0,0,.08); }

        .table-wrapper { overflow: auto; }
        .table-toolbar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin: 10px 0 8px;
        }
        .toolbar-actions { display: flex; gap: 8px; }
        .search-input {
            width: 260px;
            background: #fff;
            color: #111827;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 8px 12px;
            outline: none;
        }
        .search-input::placeholder { color: #9ca3af; }

        /* 新增：冻结前两列与可排序样式 */
        .sticky-col { position: sticky; background: white; z-index: 2; }
        .sticky-col-1 { left: 0; }
        .sticky-col-2 { left: 140px; z-index: 3; }
        .summary-table th:nth-child(1), .summary-table td:nth-child(1) { min-width: 140px; width: 140px; text-align: left; padding-left: 14px; }
        .summary-table th:nth-child(2), .summary-table td:nth-child(2) { min-width: 160px; width: 160px; text-align: left; padding-left: 14px; }
        .summary-table th.sortable { cursor: pointer; position: sticky; top: 0; }
        .summary-table th.sortable[data-sort="asc"]::after { content: " ▲"; font-size: 12px; }
        .summary-table th.sortable[data-sort="desc"]::after { content: " ▼"; font-size: 12px; }

        /* 新增：暗色模式覆盖 */
        body.dark {
            background: radial-gradient(800px 400px at 15% 0%, rgba(99,102,241,.12), transparent 60%),
                        radial-gradient(800px 400px at 85% 0%, rgba(139,92,246,.1), transparent 60%),
                        #0f172a;
            color: #e5e7eb;
        }
        body.dark .header,
        body.dark .section,
        body.dark .chart-card,
        body.dark .kpi-card { background: #111827; color: #e5e7eb; border-color: #1f2937; }
        body.dark .kpi-label { color: #9ca3af; }
        body.dark .kpi-value { color: #e5e7eb; }
        body.dark .summary-table { background: #0f1626; }
        body.dark .summary-table th { background: linear-gradient(45deg, #4f46e5, #7c3aed); color: #fff; }
        body.dark .summary-table td { background: #0f1626; color: #e5e7eb; border-color: #1f2937; }
        body.dark .summary-table tr:hover td { background: rgba(99,102,241,.12); }
        body.dark .search-input { background: #0f1626; color: #e5e7eb; border-color: #1f2937; }
        body.dark .btn { background: #1f2937; color: #e5e7eb; border-color: #374151; }
        body.dark .level-empty { background-color: rgba(156,163,175,.25) !important; color: #e5e7eb; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="header-row">
                <h1>Mythic+ 性能追踪报告</h1>
                <div class="header-actions">
                    <button id="themeToggle" class="btn">🌓 主题</button>
                </div>
            </div>
            <p>生成时间: {{GENERATION_TIME}}</p>
        </div>

        <div class="section">
            {{KPI_CARDS}}
        </div>

        {{SUMMARY_TABLE}}

        <div class="section">
            {{CHARACTER_STATS}}
        </div>

        <div class="section">
            {{DUNGEON_STATS}}
        </div>

        <div class="section">
            <h3>数据可视化</h3>
            <div class="charts-container">
                <div class="chart-card">
                    <h4>等级分布</h4>
                    <div class="chart-container">
                        <canvas id="levelChart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h4>副本表现</h4>
                    <div class="chart-container">
                        <canvas id="dungeonChart"></canvas>
                    </div>
                </div>
                <div class="chart-card">
                    <h4>职业平均层数</h4>
                    <div class="chart-container">
                        <canvas id="classChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <div class="footer">
        <p>由 Mythic Performance Tracker 自动生成</p>
    </div>

    <script>
        const chartsData = {{CHARTS_DATA}};

        // 主题切换
        (function initTheme() {
            const KEY = 'mpt-theme';
            const saved = localStorage.getItem(KEY);
            const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
            if (saved === 'dark' || (!saved && prefersDark)) {
                document.body.classList.add('dark');
            }
            const btn = document.getElementById('themeToggle');
            if (btn) {
                btn.addEventListener('click', () => {
                    document.body.classList.toggle('dark');
                    localStorage.setItem(KEY, document.body.classList.contains('dark') ? 'dark' : 'light');
                });
            }
        })();

        // 搜索与排序
        (function initSummaryTableHelpers() {
            const table = document.getElementById('summaryTable');
            if (!table) return;
            const input = document.getElementById('summarySearch');
            const clearBtn = document.getElementById('clearSearch');

            function normalizeText(s) { return (s || '').toString().toLowerCase(); }
            function filterRows() {
                const q = normalizeText(input.value);
                const rows = table.tBodies[0].rows;
                for (let i = 0; i < rows.length; i++) {
                    const cells = Array.from(rows[i].cells).map(td => normalizeText(td.textContent));
                    const ok = q === '' || cells.some(txt => txt.includes(q));
                    rows[i].style.display = ok ? '' : 'none';
                }
            }
            if (input) input.addEventListener('input', filterRows);
            if (clearBtn) clearBtn.addEventListener('click', () => { input.value = ''; filterRows(); input.focus(); });

            function parseLevel(text) {
                if (!text || text === '-') return Number.NEGATIVE_INFINITY;
                const n = parseInt(text.replace('+', ''));
                return isNaN(n) ? Number.NEGATIVE_INFINITY : n;
            }
            function sortTable(colIndex, type, asc) {
                const tbody = table.tBodies[0];
                const rows = Array.from(tbody.rows).filter(r => r.style.display !== 'none');
                const getVal = (row) => {
                    const txt = row.cells[colIndex]?.textContent?.trim() || '';
                    if (type === 'level') return parseLevel(txt);
                    if (!isNaN(parseFloat(txt)) && isFinite(txt)) return parseFloat(txt);
                    return txt.toLowerCase();
                };
                rows.sort((a,b) => { const va=getVal(a), vb=getVal(b); if (va<vb) return asc?-1:1; if (va>vb) return asc?1:-1; return 0; });
                rows.forEach(r => tbody.appendChild(r));
            }
            const headCells = table.tHead.rows[0].cells;
            let sortState = {};
            Array.from(headCells).forEach((th, i) => {
                if (!th.classList.contains('sortable')) return;
                th.addEventListener('click', () => {
                    const type = th.getAttribute('data-type') || 'text';
                    const prev = sortState[i] || false;
                    const nextAsc = !prev;
                    sortState = { [i]: nextAsc };
                    sortTable(i, type, nextAsc);
                    Array.from(headCells).forEach(h => h.removeAttribute('data-sort'));
                    th.setAttribute('data-sort', nextAsc ? 'asc' : 'desc');
                });
            });
        })();

        // 等级分布图
        const levelCtx = document.getElementById('levelChart').getContext('2d');
        new Chart(levelCtx, {
            type: 'bar',
            data: {
                labels: chartsData.level_distribution.labels,
                datasets: [{
                    label: '数量',
                    data: chartsData.level_distribution.data,
                    backgroundColor: 'rgba(102, 126, 234, 0.8)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });

        // 副本表现图
        const dungeonCtx = document.getElementById('dungeonChart').getContext('2d');
        const dungeonLabels = Object.keys(chartsData.dungeon_performance);
        const dungeonLevels = dungeonLabels.map(d => chartsData.dungeon_performance[d].avg_level);
        const dungeonTimedRates = dungeonLabels.map(d => chartsData.dungeon_performance[d].timed_rate);

        new Chart(dungeonCtx, {
            type: 'radar',
            data: {
                labels: dungeonLabels,
                datasets: [{
                    label: '平均等级',
                    data: dungeonLevels,
                    backgroundColor: 'rgba(102, 126, 234, 0.2)',
                    borderColor: 'rgba(102, 126, 234, 1)',
                    borderWidth: 2
                }, {
                    label: '限时率 (%)',
                    data: dungeonTimedRates,
                    backgroundColor: 'rgba(118, 75, 162, 0.2)',
                    borderColor: 'rgba(118, 75, 162, 1)',
                    borderWidth: 2
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    r: {
                        beginAtZero: true
                    }
                }
            }
        });

        // 职业平均层数图
        const classCtx = document.getElementById('classChart').getContext('2d');
        const classLabels = Object.keys(chartsData.class_performance);
        const classLevels = classLabels.map(c => chartsData.class_performance[c].avg_level);
        const classColors = classLabels.map(c => chartsData.class_performance[c].color || 'rgba(156,163,175,0.8)');

        new Chart(classCtx, {
            type: 'bar',
            data: {
                labels: classLabels,
                datasets: [{
                    label: '平均层数',
                    data: classLevels,
                    backgroundColor: classColors,
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: { beginAtZero: true }
                }
            }
        });
    </script>
</body>
</html>
        """
