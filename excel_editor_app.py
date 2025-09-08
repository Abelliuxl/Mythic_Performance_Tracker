import pandas as pd
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

EXCEL_FILE = 'data/character_info.xlsx' # This will be changed to character_info.xlsx later

@app.route('/')
def index():
    try:
        df = pd.read_excel(EXCEL_FILE)
        # Convert DataFrame to a list of dictionaries for easier rendering in Jinja2
        data = df.to_dict(orient='records')
        headers = df.columns.tolist()
        return render_template('index.html', headers=headers, data=enumerate(data))
    except FileNotFoundError:
        print(f"Error: Excel file not found at {EXCEL_FILE}")
        return "Error: Excel file not found. Please ensure 'data/character_info.xlsx' exists."
    except Exception as e:
        print(f"An error occurred in index route: {e}")
        return f"An error occurred: {e}"

@app.route('/save_all', methods=['POST'])
def save_all():
    try:
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
