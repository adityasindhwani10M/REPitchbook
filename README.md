Repitchbook is a full-stack real estate application prototype designed to bridge the gap between Brokers and Customers. It features a dual-interface system: a detailed listing tool for brokers empowered by AI, and a modern, "tinder-style" discovery app for customers.

Features

Broker App

Comprehensive Listing Form: Detailed intake for both "Built" properties (Apartments/Villas) and "Land" (Plots).

AI Pitch Generator: Uses Google Gemini API to generate catchy, emoji-rich sales pitches based on property details.

Local Image Upload: Supports uploading property images directly from your local drive.

Instant Database Update: Listings are saved immediately to a local SQLite database.

Customer App

Card Stack Interface: Interactive swipe-based UI for browsing properties.

Real-time Data: Fetches live listings submitted by brokers from the backend.

Advanced Filtering: Filter by budget, location, BHK, amenities, and plot size.

Match System: "Like" a property to reveal contact details.

⚙️ Backend

Python Flask Server: Handles routing, API endpoints, and database interactions.

SQLite Database: robust, serverless storage for property data (realestate.db).

Automatic Browser Launch: The app opens automatically in your default browser upon running.

Installation & Setup

1. Prerequisites

Ensure you have Python installed on your system.

2. Install Dependencies

Open your terminal or command prompt and install the required Python libraries:

pip install flask google-generativeai


3. Project Structure

Ensure your project folder (repitchbook) looks exactly like this:

repitchbook/
├── app.py                  # Main Python Flask Server
├── realestate.db           # Database (Auto-generated on first run)
├── static/
│   └── logo.png            # Your brand logo image
└── templates/
    ├── index.html          # Landing Page
    ├── broker.html         # Broker Listing App
    └── customer.html       # Customer Discovery App


4. API Key Configuration

To use the AI Pitch feature, you need a Google Gemini API key.

Open app.py.

Find the line: GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE").

Replace "YOUR_API_KEY_HERE" with your actual API key.

How to Run

Navigate to your project directory in the terminal:

cd path/to/repitchbook


Run the application:

python app.py


The server will start, and your web browser should automatically open to http://127.0.0.1:5000.

User Guide

Landing Page: Click "I'm a Broker" to list a property or "I'm a Customer" to browse.

Broker Flow:

Fill in the property details (Title, Price, Location, Type, etc.).

Upload an image from your computer.

Click "Generate Pitch" to see the AI write a sales message.

Click "Save Property" to add it to the database.

Use the "View in App" button to see how it looks to customers.

Customer Flow:

Swipe Right (♥) to "Match" (view contact info).

Swipe Left (✕) to see the next property.

Use the "Filters" button top-right to narrow down your search.

Troubleshooting

"No module named google.generativeai": You missed installing the library. Run pip install google-generativeai.

Database Errors: If the app crashes on database access, delete the realestate.db file and restart the server to let it regenerate a fresh one.

Images not showing: Ensure your image file is named logo.png and placed inside the static folder.

Built with Python, Flask, and Google Gemini.
