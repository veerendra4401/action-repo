from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
import hmac
import hashlib
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB setup
mongodb_uri = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
database_name = os.getenv('DATABASE_NAME', 'github_events')
collection_name = os.getenv('COLLECTION_NAME', 'events')

client = MongoClient(mongodb_uri)
db = client[database_name]
collection = db[collection_name]

def verify_signature(payload_body, signature_header):
    """Verify that the webhook is from GitHub"""
    if not signature_header:
        return False
    
    github_secret = os.getenv('GITHUB_SECRET')
    if not github_secret:
        return False
        
    expected_signature = 'sha1=' + hmac.new(
        github_secret.encode(),
        payload_body,
        hashlib.sha1
    ).hexdigest()
    
    return hmac.compare_digest(signature_header, expected_signature)

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle GitHub webhook events"""
    signature = request.headers.get('X-Hub-Signature')
    if not signature:
        return 'Missing signature', 401

    if not verify_signature(request.data, signature):
        return 'Invalid signature', 401

    event = request.headers.get('X-GitHub-Event')
    if not event:
        return 'Missing event type', 400

    payload = request.get_json()
    if not payload:
        return 'Invalid JSON payload', 400

    # Extract common fields
    author = payload.get('sender', {}).get('login')
    if not author:
        return 'Missing author information', 400

    timestamp = datetime.utcnow().isoformat()

    # Process different event types
    if event == 'push':
        action = 'PUSH'
        ref = payload.get('ref')
        if not ref:
            return 'Missing ref information', 400
        to_branch = ref.split('/')[-1]
        from_branch = None
    elif event == 'pull_request':
        action = 'PULL_REQUEST'
        pr = payload.get('pull_request')
        if not pr:
            return 'Missing pull request information', 400
        head = pr.get('head', {})
        base = pr.get('base', {})
        from_branch = head.get('ref')
        to_branch = base.get('ref')
        if not from_branch or not to_branch:
            return 'Missing branch information', 400
    elif event == 'pull_request_review':
        if payload.get('action') == 'submitted' and payload.get('review', {}).get('state') == 'approved':
            action = 'MERGE'
            pr = payload.get('pull_request')
            if not pr:
                return 'Missing pull request information', 400
            head = pr.get('head', {})
            base = pr.get('base', {})
            from_branch = head.get('ref')
            to_branch = base.get('ref')
            if not from_branch or not to_branch:
                return 'Missing branch information', 400
        else:
            return 'OK', 200
    else:
        return 'Event not supported', 400

    # Store in MongoDB
    document = {
        'request_id': payload.get('id', str(datetime.utcnow().timestamp())),
        'author': author,
        'action': action,
        'from_branch': from_branch,
        'to_branch': to_branch,
        'timestamp': timestamp
    }
    
    collection.insert_one(document)
    return 'OK', 200

@app.route('/events', methods=['GET'])
def get_events():
    """Get latest events from MongoDB"""
    try:
        events = list(collection.find({}, {'_id': 0}).sort('timestamp', -1).limit(10))
        return jsonify(events)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000) 