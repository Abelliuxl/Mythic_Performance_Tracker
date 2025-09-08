import pandas as pd
import json
from datetime import datetime
from config.settings import CLASS_COLOR_MAP, LAYER_COLOR_MAP, DUNGEON_NAME_MAP
from utils.logger import logger

class HTMLVisualizer:
    def __init__(self):
        self.template = self._get_html_template()
    
    def generate_html_report(self, character_info_path, result_path, output_path):
        """生成HTML可视化报告"""
        try:
            # 读取数据
            char_df = pd.read_excel(character_info_path)
            result_df = pd.read_excel(result_path, sheet_name="明细")
            
            # 生成HTML
            html_content = self._generate_html_content(char_df, result_df)
            
            # 保存文件
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.success(f"HTML可视化报告已生成: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"生成HTML报告失败: {e}")
            return False
    
    def _generate_html_content(self, char_df, result_df):
        """生成HTML内容"""
        # 准备数据
        summary_data = self._prepare_summary_data(result_df)
        character_stats = self._prepare_character_stats(char_df, result_df)
        dungeon_stats = self._prepare_dungeon_stats(result_df)
        
        # 生成图表数据
        charts_json = self._prepare_charts_data(result_df, summary_data)
        
        # 填充模板
        html_content = self.template.replace("{{TITLE}}", "Mythic+ 性能追踪报告")
        html_content = html_content.replace("{{GENERATION_TIME}}", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        html_content = html_content.replace("{{SUMMARY_TABLE}}", self._generate_summary_table(summary_data))
        html_content = html_content.replace("{{CHARACTER_STATS}}", self._generate_character_stats(character_stats))
        html_content = html_content.replace("{{DUNGEON_STATS}}", self._generate_dungeon_stats(dungeon_stats))
        html_content = html_content.replace("{{CHARTS_DATA}}", json.dumps(charts_json, ensure_ascii=False))
        
        return html_content
    
    def _prepare_summary_data(self, result_df):
        """准备总览数据"""
        pivot_df = result_df.pivot_table(
            index=["玩家", "角色名"],
            columns="副本",
            values="显示层数",
            aggfunc="first"
        ).fillna("-").reset_index()
        
        summary_data = []
        for _, row in pivot_df.iterrows():
            player_data = {
                "player": row["玩家"],
                "character": row["角色名"],
                "dungeons": {}
            }
            for dungeon in pivot_df.columns[2:]:
                player_data["dungeons"][dungeon] = row[dungeon]
            summary_data.append(player_data)
        
        return summary_data
    
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
    
    def _prepare_charts_data(self, result_df, summary_data):
        """准备图表数据"""
        charts = {
            "level_distribution": {},
            "class_performance": {},
            "dungeon_performance": {}
        }
        
        # 等级分布
        level_counts = result_df["限时层数"].value_counts().sort_index()
        charts["level_distribution"] = {
            "labels": [f"+{int(level)}" for level in level_counts.index],
            "data": level_counts.values.tolist()
        }
        
        # 职业表现
        class_performance = {}
        for _, row in result_df.iterrows():
            char_class = row["角色名"]  # 这里需要从char_df获取职业信息
            level = row["限时层数"]
            if char_class not in class_performance:
                class_performance[char_class] = []
            class_performance[char_class].append(level)
        
        for char_class, levels in class_performance.items():
            charts["class_performance"][char_class] = {
                "avg_level": round(sum(levels) / len(levels), 1),
                "count": len(levels)
            }
        
        # 副本表现
        for dungeon in result_df["副本"].unique():
            dungeon_data = result_df[result_df["副本"] == dungeon]
            charts["dungeon_performance"][dungeon] = {
                "avg_level": round(dungeon_data["限时层数"].mean(), 1),
                "timed_rate": round(len(dungeon_data[dungeon_data["是否限时"] == "是"]) / len(dungeon_data) * 100, 1)
            }
        
        return charts
    
    def _generate_summary_table(self, summary_data):
        """生成总览表格HTML"""
        html = """
        <div class="table-container">
            <h3>限时总览</h3>
            <div class="table-wrapper">
                <table class="summary-table">
                    <thead>
                        <tr>
                            <th>玩家</th>
                            <th>角色名</th>
        """
        
        # 添加副本列头
        if summary_data:
            dungeons = list(summary_data[0]["dungeons"].keys())
            for dungeon in dungeons:
                html += f"<th>{dungeon}</th>"
        
        html += """
                        </tr>
                    </thead>
                    <tbody>
        """
        
        # 添加数据行
        for player_data in summary_data:
            html += f"""
                        <tr>
                            <td>{player_data["player"]}</td>
                            <td>{player_data["character"]}</td>
            """
            for dungeon in dungeons:
                level = player_data["dungeons"][dungeon]
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
            class_color = CLASS_COLOR_MAP.get(stat["class"], "#FFFFFF")
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
            color: #999;
        }

        """ + "\n".join([f"""
        .level-{level} {{
            background-color: #{color} !important;
            color: white;
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
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Mythic+ 性能追踪报告</h1>
            <p>生成时间: {{GENERATION_TIME}}</p>
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
            </div>
        </div>
    </div>

    <div class="footer">
        <p>由 Mythic Performance Tracker 自动生成</p>
    </div>

    <script>
        const chartsData = {{CHARTS_DATA}};

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
    </script>
</body>
</html>
        """
