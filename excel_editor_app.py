import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
import hashlib
from config.settings import CLASS_COLOR_MAP # 导入职业颜色映射

app = Flask(__name__)

EXCEL_FILE = 'data/character_info.xlsx' # This will be changed to character_info.xlsx later
PASSWORD = "131415" # 请将此处的your_password_here替换为实际密码

def string_to_hsl_color(s, alpha=1.0):
    """Generates a consistent HSL color from a string."""
    hash_value = int(hashlib.sha1(s.encode('utf-8')).hexdigest(), 16)
    h = hash_value % 360
    # Use fixed saturation and lightness for pastel colors
    # s = 70 # Saturation
    # l = 80 # Lightness
    # return f"hsla({h}, {s}%, {l}%, {alpha})"
    return f"hsla({h}, 70%, 80%, {alpha + 0.1})" # 增加透明度，使其更浓

app.jinja_env.filters['string_to_color_hsl_alpha'] = string_to_hsl_color



@app.route('/')
def index():
    try:
        df = pd.read_excel(EXCEL_FILE)
        # Convert DataFrame to a list of dictionaries for easier rendering in Jinja2
        data = df.to_dict(orient='records')
        headers = df.columns.tolist()
        
        # 获取所有唯一的职业值，从配置文件中获取
        professions = sorted(CLASS_COLOR_MAP.keys())

        return render_template('index.html', headers=headers, data=enumerate(data), professions=professions)
    except FileNotFoundError:
        print(f"Error: Excel file not found at {EXCEL_FILE}")
        return "Error: Excel file not found. Please ensure 'data/character_info.xlsx' exists."
    except Exception as e:
        print(f"An error occurred in index route: {e}")
        return f"An error occurred: {e}"

@app.route('/save_all', methods=['POST'])
def save_all():
    try:
        # 获取请求中的密码
        provided_password = request.headers.get('X-Password') # 假设密码通过X-Password头传递
        if provided_password != PASSWORD:
            return "Unauthorized: Invalid password", 401

        data = request.get_json()
        if not data:
            return "No data received", 400
        
        df = pd.DataFrame(data)
        df.to_excel(EXCEL_FILE, index=False)
        print("All changes saved to Excel.")
        return "Changes saved successfully", 200
    except Exception as e:
        print(f"An error occurred while saving all: {e}")
        return f"An error occurred while saving all: {e}", 500

if __name__ == '__main__':
    print(f"Starting Flask app on http://0.0.0.0:5001 with Excel file: {EXCEL_FILE}")
    app.run(debug=True, host='0.0.0.0', port=5001)
