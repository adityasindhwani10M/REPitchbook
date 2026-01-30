import sqlite3
import json
import os
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
# Replace with your actual API Key if you have one, or set it in your environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")

if GEMINI_API_KEY != "YOUR_API_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)

# --- DATABASE SETUP ---
DB_FILE = 'realestate.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # We store the bulk of the form data in a JSON column for flexibility
    c.execute('''
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            location TEXT,
            price TEXT,
            type TEXT,
            json_data TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Initialize DB on startup
init_db()

# --- ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/broker')
def broker():
    return render_template('broker.html')

@app.route('/customer')
def customer():
    return render_template('customer.html')

# --- API ENDPOINTS ---

@app.route('/api/properties', methods=['GET', 'POST'])
def handle_properties():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    if request.method == 'POST':
        data = request.json
        # Extract core fields for SQL columns, store rest in json_data
        c.execute('''
            INSERT INTO properties (title, location, price, type, json_data)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            data.get('title'),
            data.get('location'),
            data.get('price'),
            data.get('type'),
            json.dumps(data)
        ))
        conn.commit()
        prop_id = c.lastrowid
        conn.close()
        return jsonify({"status": "success", "id": prop_id}), 201

    else: # GET
        c.execute('SELECT * FROM properties ORDER BY id DESC')
        rows = c.fetchall()
        results = []
        for row in rows:
            # Merge SQL columns with the JSON blob
            prop_data = json.loads(row['json_data'])
            prop_data['id'] = row['id']
            results.append(prop_data)
        conn.close()
        return jsonify(results)

@app.route('/api/pitch', methods=['POST'])
def generate_pitch():
    data = request.json
    
    if GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        return jsonify({"pitch": "⚠️ API Key missing in app.py. Please add your Gemini API Key to generate real pitches."})

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        prompt = f"""
        Act as a professional Real Estate Broker in India. Write a catchy, professional sales pitch for WhatsApp and Listing portals.
        
        Property Details:
        Title: {data.get('title')}
        Location: {data.get('location')}
        Price: {data.get('price')}
        Type: {data.get('type')}
        Notes: {data.get('description')}
        
        Keep it engaging, use emojis, and structure it clearly.
        """
        response = model.generate_content(prompt)
        return jsonify({"pitch": response.text})
    except Exception as e:
        print(f"AI Error: {e}")
        return jsonify({"pitch": "Error generating pitch. Please check server logs."})

if __name__ == '__main__':
    # Creates 'templates' folder if it doesn't exist (helpful for first run organization)
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("-------------------------------------------------------")
    print("Server running! Open http://127.0.0.1:5000 in your browser")
    print("Ensure index.html, broker.html, customer.html are in the 'templates' folder.")
    print("-------------------------------------------------------")
    app.run(debug=True, port=5000)
