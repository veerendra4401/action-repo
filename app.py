"""
GitHub Events Monitor

This Flask application monitors GitHub webhook events and displays them in real-time.
It supports monitoring of push events, pull requests, and merge events.

Environment Variables:
    MONGODB_URI: MongoDB connection string (default: mongodb://localhost:27017/)
    GITHUB_SECRET: GitHub webhook secret for payload verification

Repositories:
    - Action Repository: https://github.com/veerendra4401/webook.git (for GitHub Actions)
    - Webhook Repository: https://github.com/veerendra4401/webhook-repo.git (main application code)
"""

import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import pytz
import hmac
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask application
app = Flask(__name__)

# MongoDB configuration
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
DB_NAME = 'github_events'
COLLECTION_NAME = 'events'

# GitHub webhook secret
GITHUB_SECRET = os.getenv('GITHUB_SECRET', '')

# Initialize MongoDB connection
try:
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    events_collection = db[COLLECTION_NAME]
    print("Successfully connected to MongoDB!")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    raise

def verify_github_signature(payload_body, signature_header):
    """
    Verify that the webhook payload is from GitHub using the secret token.
    
    Args:
        payload_body: The raw request body
        signature_header: The signature from GitHub's X-Hub-Signature header
        
    Returns:
        bool: True if signature is valid, False otherwise
    """
    if not GITHUB_SECRET or not signature_header:
        return False
        
    expected_signature = 'sha1=' + hmac.new(
        GITHUB_SECRET.encode(),
        payload_body,
        hashlib.sha1
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)

def get_current_time():
    """
    Get current time in IST (Indian Standard Time).
    
    Returns:
        str: Current timestamp in ISO format with timezone information
    """
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).isoformat()

def clean_old_events():
    """
    Remove events older than 24 hours to maintain data freshness.
    """
    cutoff_time = datetime.now(pytz.UTC) - timedelta(hours=24)
    events_collection.delete_many({
        'timestamp': {'$lt': cutoff_time.isoformat()}
    })

@app.route('/')
def index():
    """
    Render the main page with GitHub events.
    
    Returns:
        str: Rendered HTML template with events data
    """
    try:
        # Clean old events before displaying
        clean_old_events()
        
        # Get all events sorted by timestamp in descending order
        events = list(events_collection.find().sort('timestamp', -1))
        
        # Convert ObjectId to string for JSON serialization
        for event in events:
            event['_id'] = str(event['_id'])
            # Convert action to lowercase for template
            event['action'] = event['action'].lower() if event.get('action') else ''
            
        return render_template('index.html', events=events)
    except Exception as e:
        return render_template('index.html', events=[], error=str(e))

@app.route('/webhook', methods=['POST'])
def webhook():
    """
    Handle incoming GitHub webhook events.
    
    Supported events:
    - Push events
    - Pull request events
    - Merge events (when a pull request is merged)
    
    Returns:
        tuple: JSON response and HTTP status code
    """
    try:
        # Verify GitHub signature
        signature = request.headers.get('X-Hub-Signature')
        if not verify_github_signature(request.get_data(), signature):
            return jsonify({'error': 'Invalid signature'}), 401
            
        data = request.json or {}
        event_type = request.headers.get('X-GitHub-Event', '')
        current_time = get_current_time()
        
        # Extract relevant information from the webhook payload
        event = {
            'request_id': '',
            'author': data.get('sender', {}).get('login', ''),
            'action': 'unknown',
            'from_branch': '',
            'to_branch': '',
            'timestamp': current_time,
            'repository': data.get('repository', {}).get('full_name', '')
        }

        if event_type == 'push':
            event.update({
                'request_id': data.get('after', ''),
                'action': 'push',
                'to_branch': data.get('ref', '').replace('refs/heads/', ''),
                'timestamp': current_time
            })
        elif event_type == 'pull_request':
            pr_data = data.get('pull_request', {})
            action = data.get('action', '')
            
            # Handle merged pull requests
            if action == 'closed' and pr_data.get('merged'):
                event.update({
                    'request_id': str(pr_data.get('id', '')),
                    'action': 'merge',
                    'from_branch': pr_data.get('head', {}).get('ref', ''),
                    'to_branch': pr_data.get('base', {}).get('ref', ''),
                    'timestamp': current_time
                })
            elif action in ['opened', 'reopened', 'synchronize']:
                event.update({
                    'request_id': str(pr_data.get('id', '')),
                    'action': 'pull_request',
                    'from_branch': pr_data.get('head', {}).get('ref', ''),
                    'to_branch': pr_data.get('base', {}).get('ref', ''),
                    'timestamp': current_time
                })
        
        # Only store valid events
        if event['action'] != 'unknown':
            events_collection.insert_one(event)
        
        return jsonify({'status': 'success', 'event_type': event['action']}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/events', methods=['GET'])
def get_events():
    """
    API endpoint to get all events.
    
    Returns:
        tuple: JSON response with events data and HTTP status code
    """
    try:
        clean_old_events()
        events = list(events_collection.find().sort('timestamp', -1))
        for event in events:
            event['_id'] = str(event['_id'])
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)