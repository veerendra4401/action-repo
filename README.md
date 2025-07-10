# Webhook Receiver for GitHub Actions

This repository contains a Flask application that receives GitHub webhooks and displays repository actions in real-time.

## Features

- Receives GitHub webhooks for:
  - Push events
  - Pull Request events
  - Merge events (Brownie Points)
- Stores action data in MongoDB
- Real-time UI updates (15-second polling)
- Clean and minimal design

## Message Formats

1. Push Events:
   ```
   "Travis" pushed to "staging" on 1st April 2021 - 9:30 PM UTC
   ```

2. Pull Request Events:
   ```
   "Travis" submitted a pull request from "staging" to "master" on 1st April 2021 - 9:00 AM UTC
   ```

3. Merge Events:
   ```
   "Travis" merged branch "dev" to "master" on 2nd April 2021 - 12:00 PM UTC
   ```

## Prerequisites

- Python 3.7+
- MongoDB
- Git

## Setup

1. Clone the repository:
   ```bash
   git clone <your-webhook-repo-url>
   cd webhook-repo
   ```

2. Create and activate virtual environment:
   ```bash
   python -m venv venv
   # On Windows:
   .\venv\Scripts\activate
   # On Unix or MacOS:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file:
   ```
   MONGODB_URI=mongodb://localhost:27017/
   FLASK_APP=app.py
   FLASK_ENV=development
   FLASK_DEBUG=1
   PORT=5000
   HOST=0.0.0.0
   ```

5. Start MongoDB:
   - Make sure MongoDB is running on your system
   - Default connection: mongodb://localhost:27017/

6. Run the application:
   ```bash
   python app.py
   ```

## MongoDB Schema

```json
{
    "request_id": "string (commit hash or PR ID)",
    "author": "string (GitHub username)",
    "action": "string (PUSH/PULL_REQUEST/MERGE)",
    "timestamp": "string (ISO format UTC)",
    "from_branch": "string (source branch, null for push)",
    "to_branch": "string (target branch)",
    "formatted_message": "string (formatted display message)"
}
```

## API Endpoints

- `GET /` - Web UI
- `POST /webhook` - GitHub webhook endpoint
- `GET /actions` - Get latest actions (JSON)

## Testing

1. Start the server
2. Configure webhook in action-repo:
   - Go to action-repo Settings > Webhooks
   - Add webhook:
     - Payload URL: `http://your-domain:5000/webhook`
     - Content Type: `application/json`
     - Events: Push and Pull requests

## Development

The application is structured as follows:
```
webhook-repo/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
├── .gitignore         # Git ignore rules
├── README.md          # This file
└── templates/         # HTML templates
    └── index.html     # Main UI template
```

## Production Deployment

For production:
1. Use a production-grade WSGI server (e.g., Gunicorn)
2. Set up proper MongoDB authentication
3. Use HTTPS for webhook endpoint
4. Set `FLASK_ENV=production` and `FLASK_DEBUG=0` 