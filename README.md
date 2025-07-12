# GitHub Webhook Monitor

This application monitors GitHub repository events using webhooks and displays them in real-time through a web interface.

## Features

- Monitors GitHub repository events (Push, Pull Request, Merge)
- Stores event data in MongoDB
- Real-time UI updates (15-second polling)
- Supports multiple event types with formatted display
- Secure webhook handling with signature verification
- Detailed event logging and monitoring
- Automatic timestamp conversion to UTC
- Beautiful and responsive UI design

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env`:
   ```
   MONGODB_URI=your_mongodb_connection_string
   GITHUB_SECRET=your_webhook_secret
   DATABASE_NAME=github_events
   COLLECTION_NAME=events
   ```

3. Configure GitHub webhook:
   - Go to repository settings
   - Add webhook with URL: `http://your-domain/webhook` (important: include /webhook at the end)
   - Set content type to `application/json`
   - Set secret to match your `GITHUB_SECRET`
   - Select events: Push, Pull Request

4. Run the application:
   ```bash
   python app.py
   ```

## Project Structure

- `app.py` - Main Flask application with webhook handling
- `templates/` - HTML templates for the UI
- `static/` - Static assets (CSS, JS)
- `.env` - Environment variables configuration
- `requirements.txt` - Python package dependencies

## Event Formats

- Push: "{author} pushed to {to_branch} on {timestamp}"
- Pull Request: "{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"
- Merge: "{author} merged branch {from_branch} to {to_branch} on {timestamp}"

## Testing Webhook

The webhook endpoint expects:
- POST requests to `/webhook`
- Valid GitHub signature in `X-Hub-Signature` header
- JSON payload with event details

## Troubleshooting

Common webhook issues:
- Ensure the webhook URL ends with `/webhook`
- Verify the content type is set to `application/json`
- Check that the webhook secret matches your `.env` file
- Monitor the application logs for detailed error messages

## Security Features

- HMAC signature verification for webhooks
- Environment-based configuration
- Input validation and sanitization
- Error handling and logging
- Secure data transmission
- Rate limiting protection 