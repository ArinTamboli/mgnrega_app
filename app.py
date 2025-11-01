from flask import Flask, render_template, jsonify
import requests, sqlite3, json, os

app = Flask(__name__)

conn = sqlite3.connect('mgnrega.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS data (district TEXT PRIMARY KEY, json TEXT)')
conn.commit()

API_URL = "https://api.data.gov.in/resource/f5a6f7e1-7b2b-4ac1-b8e2-02cbdc14fa3e?api-key=579b464db66ec23bdd000001b3d5fffb7fc5495e63a3dc9073cc2b62&format=json"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/data/<district>')
def get_data(district):
    c.execute("SELECT json FROM data WHERE district=?", (district,))
    row = c.fetchone()
    if row:
        print("Serving cached data for:", district)
        return row[0]

    print("Fetching new data from API for:", district)
    response = requests.get(API_URL + "&filters[district_name]=" + district)
    if response.status_code != 200:
        return jsonify({"error": "API not available"}), 500

    data = response.json()
    c.execute("INSERT OR REPLACE INTO data VALUES (?, ?)", (district, json.dumps(data)))
    conn.commit()
    return jsonify(data)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
