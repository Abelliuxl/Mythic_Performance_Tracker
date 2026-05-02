import pandas as pd
import re
import json
import time
from urllib.parse import quote
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from config.settings import (
    DUNGEON_NAME_MAP, DUNGEON_TIME_LIMIT,
    BLIZZARD_BASE_URL, BLIZZARD_API_BASE,
    SERVER_SLUG_MAP
)
from utils.logger import logger


class DataProcessor:
    @staticmethod
    def load_character_data(file_path):
        try:
            char_df = pd.read_excel(file_path)
            logger.success(f"成功读取角色文件: {file_path}")
            return char_df
        except Exception as e:
            logger.error(f"无法读取角色文件 {file_path}: {e}")
            return None

    @staticmethod
    def get_server_slug(server_name):
        server_name = str(server_name).strip()
        slug = SERVER_SLUG_MAP.get(server_name)
        if slug:
            return slug
        logger.warning(f"未找到服务器 '{server_name}' 的英文slug，尝试直接使用原始名称")
        return quote(server_name, safe="")

    @staticmethod
    def build_character_url(server_name, character_name):
        slug = DataProcessor.get_server_slug(server_name)
        encoded_name = quote(character_name.strip(), safe="")
        return f"{BLIZZARD_BASE_URL}#/{slug}/{encoded_name}?q={encoded_name}"

    @staticmethod
    def wait_for_mytable_data(driver, timeout=15):
        wait = WebDriverWait(driver, timeout)
        logger.info("等待页面加载 M+ 数据...")

        selectors = [
            ".mythic-keystone", ".MythicKeystone", "[class*='mythic']",
            "[class*='keystone']", ".dungeon-run", ".MythicKeystoneDungeonRun",
            ".stone-slide", "[class*='dungeon']",
            ".el-table", ".el-table__body",
            ".pve-content", "[class*='pve']",
            ".role-info", ".character-info",
        ]

        for selector in selectors:
            try:
                element = wait.until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
                logger.info(f"找到元素: {selector}")
                return selector
            except TimeoutException:
                continue

        logger.warning("未找到已知的M+数据元素")
        return None

    @staticmethod
    def extract_json_from_attrs(driver):
        records = []
        js_code = """
        var results = [];
        var patterns = ['mythic_keystone', 'mythicRating', 'mythic_rating', 'dungeonData', 'dungeon_data'];
        for (var i = 0; i < patterns.length; i++) {
            var els = document.querySelectorAll('[data-' + patterns[i] + '], [' + patterns[i] + ']');
            for (var j = 0; j < els.length; j++) {
                var val = els[j].getAttribute(patterns[i]) || els[j].getAttribute('data-' + patterns[i]);
                if (val) { results.push(val); }
            }
        }
        return results;
        """
        try:
            raw = driver.execute_script(js_code)
            for item in raw:
                try:
                    data = json.loads(item)
                    records.extend(DataProcessor._normalize_mplus_data(data))
                except (json.JSONDecodeError, TypeError):
                    continue
        except Exception as e:
            logger.debug(f"从 data-attr 提取数据失败: {e}")
        return records

    @staticmethod
    def extract_vuex_data(driver):
        records = []
        js_code = """
        try {
            var app = document.querySelector('#app');
            if (app && app.__vue_app__) {
                var store = app.__vue_app__.config.globalProperties.$store;
                if (store && store.state) {
                    return JSON.stringify(store.state);
                }
            }
            var el = document.querySelector('#app');
            if (el && el.__vue__ && el.__vue__.$store && el.__vue__.$store.state) {
                return JSON.stringify(el.__vue__.$store.state);
            }
        } catch(e) {}
        return null;
        """
        try:
            state_json = driver.execute_script(js_code)
            if state_json:
                state = json.loads(state_json)
                records.extend(DataProcessor._extract_from_state(state))
        except Exception as e:
            logger.debug(f"从 Vuex store 提取数据失败: {e}")
        return records

    @staticmethod
    def _extract_from_state(state):
        records = []
        if isinstance(state, dict):
            for key in ["mythicKeystone", "mythic_keystone", "pve", "dungeon"]:
                data = state.get(key, state.get(f"{key}Data", state.get(f"{key}Info")))
                if data:
                    result = DataProcessor._normalize_mplus_data(data)
                    if result:
                        records.extend(result)
        return records

    @staticmethod
    def _normalize_mplus_data(data):
        records = []
        if isinstance(data, dict):
            runs = data.get("runs", data.get("dungeon_runs", data.get("bestRuns", [])))
            if isinstance(runs, list):
                for run in runs:
                    record = DataProcessor._parse_run(run)
                    if record:
                        records.append(record)
            else:
                record = DataProcessor._parse_run(data)
                if record:
                    records.append(record)
        elif isinstance(data, list):
            for item in data:
                record = DataProcessor._parse_run(item)
                if record:
                    records.append(record)
        return records

    @staticmethod
    def _parse_run(run):
        if not isinstance(run, dict):
            return None

        dungeon_raw = (run.get("dungeon") or {}).get("name",
                       run.get("dungeon_name", run.get("name", "")))
        dungeon = DUNGEON_NAME_MAP.get(dungeon_raw, dungeon_raw)

        level = run.get("keystone_level", run.get("level",
                        run.get("mythic_level", run.get("plus_level"))))

        time_str = run.get("clear_time", run.get("time",
                        run.get("run_time", run.get("duration", ""))))
        if isinstance(time_str, (int, float)):
            minutes = int(time_str // 60)
            seconds = int(time_str % 60)
            time_str = f"{minutes:02d}:{seconds:02d}"
        elif isinstance(time_str, str) and not re.match(r"\d{1,2}:\d{2}", time_str):
            time_seconds = run.get("clear_time_ms", 0) or run.get("duration_ms", 0) or 0
            if time_seconds > 0:
                time_seconds = time_seconds / 1000 if time_seconds > 10000 else time_seconds
                minutes = int(time_seconds / 60)
                seconds = int(time_seconds % 60)
                time_str = f"{minutes:02d}:{seconds:02d}"

        if not re.match(r"\d{1,2}:\d{2}", str(time_str)):
            time_str = None

        if time_str and dungeon:
            t_split = time_str.split(":")
            run_seconds = int(t_split[0]) * 60 + int(t_split[1]) if len(t_split) == 2 else 9999
            limit = DUNGEON_TIME_LIMIT.get(dungeon)
            on_time = (limit is not None and run_seconds <= limit)
            result = "是" if on_time else "否"

            level_str = run.get("keystone_level", run.get("level",
                              run.get("mythic_level", run.get("plus_level"))))
            try:
                level_int = int(level_str) if level_str is not None else None
            except (ValueError, TypeError):
                level_int = None

            return {
                "副本": dungeon,
                "限时层数": level_int,
                "通关时间": time_str,
                "是否限时": result,
            }

        return None

    @staticmethod
    def parse_dungeon_data(row_soup, dungeon_name_map=None):
        if dungeon_name_map is None:
            dungeon_name_map = DUNGEON_NAME_MAP
        try:
            a_tag = row_soup.find("a", class_="Boss zone-boss-cell")
            if not a_tag:
                return None
            raw_dungeon = a_tag.text.strip()
            dungeon = dungeon_name_map.get(raw_dungeon, raw_dungeon)
            time_cells = row_soup.find_all("td", class_="verbose main-table-number kills-cell")
            if len(time_cells) < 2:
                return None
            time_text = time_cells[1].get_text(strip=True)
            time_match = re.search(r"\d{1,2}:\d{2}", time_text)
            time_str = time_match.group(0) if time_match else "未知"
            level_match = re.search(r"\+(\d+)", time_text)
            plus_level = int(level_match.group(1)) if level_match else None
            t_split = time_str.split(":")
            run_seconds = int(t_split[0]) * 60 + int(t_split[1]) if len(t_split) == 2 else 9999
            limit = DUNGEON_TIME_LIMIT.get(dungeon)
            on_time = (limit is not None and run_seconds <= limit)
            result = "是" if on_time else "否"
            return {
                "副本": dungeon,
                "限时层数": plus_level,
                "通关时间": time_str,
                "是否限时": result,
            }
        except Exception as e:
            logger.error(f"解析副本行失败: {e}")
            return None

    @staticmethod
    def extract_mplus_from_dom(driver):
        records = []
        js_code = """
        var results = [];
        var slides = document.querySelectorAll('.stone-slide');
        slides.forEach(function(slide) {
            var text = slide.innerText || '';
            var lines = text.split('\\n').filter(function(l) { return l.trim(); });
            if (lines.length >= 3) {
                results.push({
                    level: lines[0].trim(),
                    dungeon: lines[1].trim(),
                    time: lines[2].trim(),
                });
            }
        });
        return results;
        """
        try:
            raw_data = driver.execute_script(js_code)
            seen = set()
            for item in raw_data:
                key = (item["dungeon"], item["level"])
                if key in seen:
                    continue
                seen.add(key)

                dungeon = item["dungeon"]
                time_str = item["time"]
                level_str = item["level"]

                if not re.match(r"\d{1,2}:\d{2}", time_str):
                    continue

                try:
                    level_int = int(level_str)
                except (ValueError, TypeError):
                    continue

                records.append({
                    "副本": dungeon,
                    "限时层数": level_int,
                    "通关时间": time_str,
                    "是否限时": "是",
                })

            if records:
                logger.info(f"从 DOM 结构提取到 {len(records)} 条大秘境记录")
            return records
        except Exception as e:
            logger.debug(f"DOM 提取失败: {e}")
            return records

    @staticmethod
    def extract_mplus_from_page_text(driver):
        records = []
        js_code = """
        var bodyText = document.body.innerText || '';
        var lines = bodyText.split('\\n').filter(function(l) { return l.trim(); });
        return lines.slice(0, 500);
        """
        try:
            lines = driver.execute_script(js_code)
            dungeon_names_cn = list(DUNGEON_NAME_MAP.values())
            dungeon_names_en = list(DUNGEON_NAME_MAP.keys())
            all_dungeon_names = dungeon_names_cn + dungeon_names_en

            current_dungeon = None
            for line in lines:
                line = line.strip()
                for dn in all_dungeon_names:
                    if dn in line or (DUNGEON_NAME_MAP.get(dn) and DUNGEON_NAME_MAP[dn] in line):
                        dungeon_key = dn if dn in DUNGEON_NAME_MAP else (
                            next((k for k, v in DUNGEON_NAME_MAP.items() if v == dn), dn))
                        current_dungeon = DUNGEON_NAME_MAP.get(dungeon_key, dungeon_key)
                        break

                if current_dungeon:
                    level_match = re.search(r"[+](\d+)", line)
                    time_match = re.search(r"(\d{1,2}:\d{2})", line)
                    if level_match and time_match:
                        try:
                            level = int(level_match.group(1))
                            time_str = time_match.group(1)
                            t_split = time_str.split(":")
                            run_seconds = int(t_split[0]) * 60 + int(t_split[1])
                            limit = DUNGEON_TIME_LIMIT.get(current_dungeon)
                            on_time = (limit is not None and run_seconds <= limit)
                            result = "是" if on_time else "否"
                            records.append({
                                "副本": current_dungeon,
                                "限时层数": level,
                                "通关时间": time_str,
                                "是否限时": result,
                            })
                            current_dungeon = None
                        except (ValueError, IndexError):
                            pass
        except Exception as e:
            logger.debug(f"从页面文本提取数据失败: {e}")
        return records

    @staticmethod
    def extract_mplus_via_api_call(driver, realm_slug, role_name):
        records = []
        script = f"""
        var xhr = new XMLHttpRequest();
        xhr.open('GET', '{BLIZZARD_API_BASE}/do?realmSlug={realm_slug}&roleName={quote(role_name)}', false);
        xhr.withCredentials = true;
        xhr.send();
        return xhr.responseText;
        """
        try:
            time.sleep(1)
            result = driver.execute_script(script)
            if result:
                data = json.loads(result)
                logger.info(f"API /do 响应: {json.dumps(data, ensure_ascii=False)[:500]}")
        except Exception as e:
            logger.debug(f"API 调用失败: {e}")
        return records

    @staticmethod
    def format_display_level(row):
        lvl = row["限时层数"]
        if pd.isna(lvl):
            return "-"
        return f"+{int(lvl)}" if row["是否限时"] == "是" else f"+{int(lvl)}*"

    @staticmethod
    def create_pivot_table(df):
        pivot_df = df.pivot_table(
            index=["玩家", "角色名"],
            columns="副本",
            values="显示层数",
            aggfunc="first"
        ).fillna("-").reset_index()
        return pivot_df

    @staticmethod
    def validate_character_data(char_df):
        required_columns = ["玩家", "角色名", "服务器", "职业"]
        missing_columns = [col for col in required_columns if col not in char_df.columns]
        if missing_columns:
            logger.error(f"角色数据缺少必要列: {missing_columns}")
            return False
        for col in required_columns:
            if char_df[col].isnull().any():
                logger.error(f"角色数据列 '{col}' 存在空值")
                return False
        logger.success("角色数据格式验证通过")
        return True

    @staticmethod
    def clean_character_name(name):
        return str(name).strip()

    @staticmethod
    def clean_server_name(server):
        return str(server).strip()

    @staticmethod
    def get_character_class_map(char_df):
        return dict(zip(char_df["角色名"], char_df["职业"]))

    @staticmethod
    def standardize_class_names(char_df):
        if "职业" in char_df.columns:
            char_df["职业"] = char_df["职业"].replace("潜行者", "盗贼")
            logger.info("已将职业名称中的'潜行者'统一替换为'盗贼'")
        return char_df

    @staticmethod
    def extract_window_data_vue(driver):
        records = []
        try:
            vue_data = driver.execute_script("""
            try {
                var el = document.querySelector('#app');
                if (!el) return null;
                var vm = el.__vue__ || el.__vue_app__;
                if (!vm) return null;
                var data = {};
                if (vm.$data) Object.assign(data, vm.$data);
                if (vm.setupState) Object.assign(data, vm.setupState);
                return JSON.stringify(data);
            } catch(e) { return null; }
            """)
            if vue_data:
                data = json.loads(vue_data)
                records.extend(DataProcessor._normalize_mplus_data(data))
        except Exception as e:
            logger.debug(f"Vue data 提取失败: {e}")
        return records
