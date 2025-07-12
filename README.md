# GitHub Webhook Receiver

This Flask application receives and displays GitHub webhook events in real-time. It supports monitoring of push events, pull requests, and merge events.

## Features

- Real-time webhook event processing
- MongoDB storage for event persistence
- Clean, modern UI with 15-second auto-refresh
- Secure webhook validation
- Support for Push, Pull Request, and Merge events

## Event Display Format

The application displays events in the following format:

1. For Push events:
   ```
   "Travis" pushed to "staging" on 1st April 2021 - 9:30 PM UTC
   ```

2. For Pull Request events:
   ```
   "Travis" submitted a pull request from "staging" to "master" on 1st April 2021 - 9:00 AM UTC
   ```

3. For Merge events:
   ```
   "Travis" merged branch "dev" to "master" on 2nd April 2021 - 12:00 PM UTC
   ```

## Setup Instructions

1. **Prerequisites**
   - Python 3.8+
   - MongoDB 4.0+
   - pip (Python package manager)

2. **Installation**
   ```bash
   # Clone the repository
   git clone <your-repo-url>
   cd webhook-repo

   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Configuration**
   Create a `.env` file in the root directory with the following variables:
   ```
   MONGODB_URI=mongodb://localhost:27017/
   GITHUB_SECRET=your-webhook-secret
   ```

4. **MongoDB Setup**
   - Start MongoDB service
   - The application will automatically:
     - Create a database named `github_events`
     - Create a collection named `events`
     - Handle schema validation

5. **Running the Application**
   ```bash
   python app.py
   ```
   The application will start on `http://localhost:5000`

6. **Webhook Configuration**
   In your GitHub repository:
   1. Go to Settings → Webhooks → Add webhook
   2. Set Payload URL to `http://your-domain/webhook`
   3. Set Content type to `application/json`
   4. Set Secret to match your `GITHUB_SECRET`
   5. Select events:
      - Push
      - Pull requests

## MongoDB Schema

The application uses the following MongoDB schema for events:

```json
{
  "request_id": "string",
  "author": "string",
  "action": "string",
  "from_branch": "string",
  "to_branch": "string",
  "timestamp": "string",
  "repository": "string"
}
```

## API Endpoints

1. `GET /`
   - Renders the main UI
   - Displays all events in chronological order
   - Auto-refreshes every 15 seconds

2. `POST /webhook`
   - Receives GitHub webhook events
   - Validates webhook signature
   - Processes and stores events

3. `GET /events`
   - Returns JSON array of all events
   - Used by UI for polling updates

## Security Features

1. **Webhook Validation**
   - SHA1 HMAC signature verification
   - Configurable secret token
   - Request validation before processing

2. **MongoDB Security**
   - Connection string validation
   - Error handling for connection issues
   - Automatic reconnection handling

## Error Handling

1. **MongoDB Connection**
   - Graceful handling of connection failures
   - Clear error messages in UI
   - Automatic reconnection attempts

2. **Webhook Processing**
   - Invalid signature detection
   - Malformed payload handling
   - Detailed error logging

## Development

1. **Running Tests**
   ```bash
   # Install test dependencies
   pip install -r requirements-dev.txt

   # Run tests
   python -m pytest
   ```

2. **Local Development**
   ```bash
   # Run with debug mode
   FLASK_ENV=development python app.py
   ```

3. **Code Style**
   ```bash
   # Install linting tools
   pip install flake8 black

   # Run linters
   flake8 .
   black .
   ```

## Troubleshooting

1. **MongoDB Connection Issues**
   - Verify MongoDB is running
   - Check connection string in `.env`
   - Ensure network connectivity

2. **Webhook Not Receiving Events**
   - Verify webhook URL is accessible
   - Check GitHub webhook configuration
   - Validate webhook secret

3. **UI Not Updating**
   - Clear browser cache
   - Check browser console for errors
   - Verify MongoDB connection 