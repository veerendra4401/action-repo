from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MongoDB connection with error handling
try:
    client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
    # Test the connection
    client.server_info()
    db = client['github_webhook_db']
    actions_collection = db['actions']
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

def format_timestamp(timestamp_str: str) -> str:
    """Format timestamp to match requirements: '1st April 2021 - 9:30 PM UTC'"""
    dt = datetime.fromisoformat(timestamp_str)
    day = str(dt.day)
    if day.endswith('1') and day != '11':
        day += 'st'
    elif day.endswith('2') and day != '12':
        day += 'nd'
    elif day.endswith('3') and day != '13':
        day += 'rd'
    else:
        day += 'th'
    return dt.strftime(f'{day} %B %Y - %I:%M %p UTC')

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"Error rendering index.html: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data: Dict[str, Any] = request.json if request.json else {}
        
        # Extract relevant information based on the event type
        event_type = request.headers.get('X-GitHub-Event', '')
        logger.info(f"Received webhook event: {event_type}")
        
        if not event_type or event_type not in ['push', 'pull_request']:
            return jsonify({'status': 'ignored', 'message': f'Event {event_type} not handled'}), 200

        # Initialize action_data with safe defaults
        action_data = {
            'request_id': '',
            'author': '',
            'timestamp': datetime.utcnow().isoformat(),
            'action': '',
            'to_branch': '',
            'from_branch': None,
            'formatted_message': ''
        }
        
        if event_type == 'push':
            # Handle push event
            if not data:
                logger.warning("Invalid push event data received")
                return jsonify({'status': 'error', 'message': 'Invalid push event data'}), 400
                
            author = data.get('pusher', {}).get('name', 'Unknown')
            to_branch = data.get('ref', '').split('/')[-1] if data.get('ref') else 'unknown'
            
            action_data.update({
                'request_id': data.get('after', ''),
                'author': author,
                'action': 'PUSH',
                'to_branch': to_branch,
                'formatted_message': f'"{author}" pushed to "{to_branch}"'
            })
            
        elif event_type == 'pull_request':
            # Handle pull request event
            pull_request = data.get('pull_request', {})
            if not pull_request:
                logger.warning("Invalid pull request data received")
                return jsonify({'status': 'error', 'message': 'Invalid pull request data'}), 400
                
            pr_action = data.get('action', '')
            author = pull_request.get('user', {}).get('login', 'Unknown')
            from_branch = pull_request.get('head', {}).get('ref', 'unknown')
            to_branch = pull_request.get('base', {}).get('ref', 'unknown')
            
            is_merge = pr_action == 'closed' and pull_request.get('merged', False)
            action_type = 'MERGE' if is_merge else 'PULL_REQUEST'
            
            message = (
                f'"{author}" merged branch "{from_branch}" to "{to_branch}"'
                if is_merge else
                f'"{author}" submitted a pull request from "{from_branch}" to "{to_branch}"'
            )
            
            action_data.update({
                'request_id': str(pull_request.get('id', '')),
                'author': author,
                'action': action_type,
                'from_branch': from_branch,
                'to_branch': to_branch,
                'formatted_message': message
            })
        
        # Add timestamp to formatted message
        action_data['formatted_message'] += f" on {format_timestamp(action_data['timestamp'])}"
        
        # Store in MongoDB
        actions_collection.insert_one(action_data)
        logger.info(f"Successfully stored action: {action_data['action']}")
        
        return jsonify({'status': 'success', 'data': action_data}), 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/actions', methods=['GET'])
def get_actions():
    try:
        # Get the latest actions from MongoDB
        actions = list(actions_collection.find(
            {},
            {'_id': 0}  # Exclude MongoDB _id from results
        ).sort('timestamp', -1).limit(10))  # Get latest 10 actions
        
        logger.info(f"Retrieved {len(actions)} actions")
        return jsonify(actions)
    except Exception as e:
        logger.error(f"Error retrieving actions: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')
    debug = bool(int(os.getenv('FLASK_DEBUG', 1)))
    
    logger.info(f"Starting Flask server on {host}:{port} (debug={debug})")
    app.run(host=host, port=port, debug=debug) 