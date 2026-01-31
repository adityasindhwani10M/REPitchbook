import sqlite3
import json
import os
import webbrowser
from threading import Timer
import google.generativeai as genai
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyDGo_VGC4C2TVA5d9ePzh2wKzZxIRh54dk")

if GEMINI_API_KEY != "AIzaSyDGo_VGC4C2TVA5d9ePzh2wKzZxIRh54dk":
    genai.configure(api_key=GEMINI_API_KEY)

# --- DATABASE SETUP ---
# Fix: Use absolute path to ensure DB is created/read from the correct folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, 'realestate.db')

def init_db():
    try:
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
        
        # Check if DB is empty and seed if necessary
        c.execute('SELECT count(*) FROM properties')
        count = c.fetchone()[0]
        
        if count == 0:
            print("Database is empty. Seeding with a sample property...")
            sample_data = {
                "title": "Sample: Green Valley Plot",
                "location": "Electronic City, Bangalore",
                "price": "45 Lakhs",
                "type": "Land",
                "description": "This is a sample listing from the database. It proves your backend is connected! Add your own via the Broker Page.",
                "image": "https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=500&q=80",
                "contact": {"phone": "System", "type": "Admin"}
            }
            c.execute('''
                INSERT INTO properties (title, location, price, type, json_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                sample_data['title'],
                sample_data['location'],
                sample_data['price'],
                sample_data['type'],
                json.dumps(sample_data)
            ))
            conn.commit()

        conn.close()
        print(f"Database initialized at: {DB_FILE}")
    except sqlite3.DatabaseError as e:
        print(f"Error accessing database: {e}")
        print("If you edited realestate.db manually, it might be corrupted. Delete the file and restart the app.")

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
    try:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        if request.method == 'POST':
            data = request.json
            print(f"Broker is saving property: {data.get('title')}") # Debug Log

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
            print(f"Property saved successfully! ID: {prop_id}") # Debug Log
            return jsonify({"status": "success", "id": prop_id}), 201

        else: # GET
            c.execute('SELECT * FROM properties ORDER BY id DESC')
            rows = c.fetchall()
            results = []
            for row in rows:
                # Merge SQL columns with the JSON blob
                try:
                    prop_data = json.loads(row['json_data'])
                    prop_data['id'] = row['id']
                    results.append(prop_data)
                except json.JSONDecodeError:
                    continue # Skip corrupted rows
            conn.close()
            print(f"Customer requested listings. Sending {len(results)} properties.") # Debug Log
            return jsonify(results)
    except Exception as e:
        print(f"Database Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/pitch', methods=['POST'])
def generate_pitch():
    data = request.json
    print(f"Generating AI Pitch for: {data.get('title')}") # Debug Log
    
    if GEMINI_API_KEY == "YOUR_API_KEY_HERE":
        return jsonify({"pitch": "⚠️ API Key missing in app.py. Please add your Gemini API Key to generate real pitches."})

    try:
        # Switched to 1.5-flash for better stability
        model = genai.GenerativeModel('gemini-1.5-flash')
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

def open_browser():
    """Opens the default web browser to the application URL."""
    webbrowser.open_new("http://127.0.0.1:5000")

if __name__ == '__main__':
    # Creates 'templates' folder if it doesn't exist (helpful for first run organization)
    if not os.path.exists('templates'):
        os.makedirs('templates')
    
    print("-------------------------------------------------------")
    print("Server running! Opening http://127.0.0.1:5000 in your browser...")
    print("-------------------------------------------------------")
    
    # We use a Timer to open the browser after a short delay (1.5s) to ensure the server starts first.
    if not os.environ.get("WERKZEUG_RUN_MAIN"):
        Timer(1.5, open_browser).start()

    app.run(debug=True, port=5000)
