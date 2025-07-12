"""
GitHub Events Monitor

This Flask application monitors GitHub webhook events and displays them in real-time.
It supports monitoring of push events, pull requests, and merge events.

Environment Variables:
    MONGODB_URI: MongoDB connection string (default: mongodb://localhost:27017/)
    GITHUB_SECRET: GitHub webhook secret for payload verification
"""

import os
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import pytz
import hmac
import hashlib
from dotenv import load_dotenv
from dateutil import parser

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

def get_mongodb_client():
    """Get MongoDB client with proper error handling."""
    try:
        client = MongoClient(MONGODB_URI)
        # Test the connection
        client.admin.command('ping')
        return client
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")
        return None

# Initialize MongoDB connection
client = get_mongodb_client()
if client:
    db = client[DB_NAME]
    events_collection = db[COLLECTION_NAME]
    print("Successfully connected to MongoDB!")
else:
    print("Failed to connect to MongoDB. Please check your connection string.")

def verify_github_signature(payload_body, signature_header):
    """
    Verify that the webhook payload is from GitHub using the secret token.
    """
    if not GITHUB_SECRET or not signature_header:
        return False
        
    expected_signature = 'sha1=' + hmac.new(
        GITHUB_SECRET.encode(),
        payload_body,
        hashlib.sha1
    ).hexdigest()
    
    return hmac.compare_digest(expected_signature, signature_header)

def format_timestamp(timestamp_str):
    """
    Format timestamp to match requirements: '1st April 2021 - 9:30 PM UTC'
    """
    try:
        dt = parser.parse(timestamp_str)
        dt_utc = dt.astimezone(pytz.UTC)
        
        # Get day with suffix (1st, 2nd, 3rd, etc.)
        day = dt_utc.day
        if 10 <= day % 100 <= 20:
            suffix = 'th'
        else:
            suffix = {1: 'st', 2: 'nd', 3: 'rd'}.get(day % 10, 'th')
        
        return dt_utc.strftime(f'%-d{suffix} %B %Y - %-I:%M %p UTC')
    except Exception:
        return timestamp_str

def clean_old_events():
    """Remove events older than 24 hours to maintain data freshness."""
    if not client:
        return
        
    cutoff_time = datetime.now(pytz.UTC) - timedelta(hours=24)
    events_collection.delete_many({
        'timestamp': {'$lt': cutoff_time.isoformat()}
    })

@app.route('/')
def index():
    """Render the main page with GitHub events."""
    try:
        if not client:
            return render_template('index.html', events=[], error="MongoDB connection not available")
            
        # Clean old events before displaying
        clean_old_events()
        
        # Get all events sorted by timestamp in descending order
        events = list(events_collection.find().sort('timestamp', -1))
        
        # Format events for display
        for event in events:
            event['_id'] = str(event['_id'])
            event['formatted_message'] = format_event_message(event)
            
        return render_template('index.html', events=events)
    except Exception as e:
        return render_template('index.html', events=[], error=str(e))

def format_event_message(event):
    """Format event message according to requirements."""
    timestamp = format_timestamp(event['timestamp'])
    
    if event['action'] == 'PUSH':
        return f'"{event["author"]}" pushed to "{event["to_branch"]}" on {timestamp}'
    elif event['action'] == 'PULL_REQUEST':
        return f'"{event["author"]}" submitted a pull request from "{event["from_branch"]}" to "{event["to_branch"]}" on {timestamp}'
    elif event['action'] == 'MERGE':
        return f'"{event["author"]}" merged branch "{event["from_branch"]}" to "{event["to_branch"]}" on {timestamp}'
    return ''

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming GitHub webhook events."""
    if not client:
        return jsonify({'error': 'MongoDB connection not available'}), 503
        
    try:
        # Verify GitHub signature
        signature = request.headers.get('X-Hub-Signature')
        if not verify_github_signature(request.get_data(), signature):
            return jsonify({'error': 'Invalid signature'}), 401
            
        data = request.json or {}
        event_type = request.headers.get('X-GitHub-Event', '')
        current_time = datetime.now(pytz.UTC).isoformat()
        
        # Extract relevant information from the webhook payload
        event = {
            'request_id': '',
            'author': data.get('sender', {}).get('login', ''),
            'action': 'UNKNOWN',
            'from_branch': '',
            'to_branch': '',
            'timestamp': current_time,
            'repository': data.get('repository', {}).get('full_name', '')
        }

        if event_type == 'push':
            event.update({
                'request_id': data.get('after', ''),
                'action': 'PUSH',
                'to_branch': data.get('ref', '').replace('refs/heads/', ''),
            })
        elif event_type == 'pull_request':
            pr_data = data.get('pull_request', {})
            action = data.get('action', '')
            
            # Handle merged pull requests
            if action == 'closed' and pr_data.get('merged'):
                event.update({
                    'request_id': str(pr_data.get('id', '')),
                    'action': 'MERGE',
                    'from_branch': pr_data.get('head', {}).get('ref', ''),
                    'to_branch': pr_data.get('base', {}).get('ref', ''),
                })
            elif action in ['opened', 'reopened', 'synchronize']:
                event.update({
                    'request_id': str(pr_data.get('id', '')),
                    'action': 'PULL_REQUEST',
                    'from_branch': pr_data.get('head', {}).get('ref', ''),
                    'to_branch': pr_data.get('base', {}).get('ref', ''),
                })
        
        # Only store valid events
        if event['action'] != 'UNKNOWN':
            events_collection.insert_one(event)
            event['formatted_message'] = format_event_message(event)
        
        return jsonify({'status': 'success', 'event': event}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/events', methods=['GET'])
def get_events():
    """API endpoint to get all events."""
    if not client:
        return jsonify({'error': 'MongoDB connection not available'}), 503
        
    try:
        clean_old_events()
        events = list(events_collection.find().sort('timestamp', -1))
        
        # Format events for display
        for event in events:
            event['_id'] = str(event['_id'])
            event['formatted_message'] = format_event_message(event)
            
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)