# GitHub Webhook Monitor

This application monitors GitHub repository events using webhooks and displays them in real-time through a web interface.

## Features

- Monitors GitHub repository events (Push, Pull Request, Merge)
- Stores event data in MongoDB
- Real-time UI updates (15-second polling)
- Supports multiple event types with formatted display

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env`:
   ```
   MONGODB_URI=your_mongodb_connection_string
   GITHUB_SECRET=your_webhook_secret
   ```

3. Configure GitHub webhook:
   - Go to your repository settings
   - Add webhook with URL: `http://your-domain/webhook`
   - Set content type to `application/json`
   - Set secret to match your `GITHUB_SECRET`
   - Select events: Push, Pull Request

4. Run the application:
   ```bash
   python app.py
   ```

## Project Structure

- `app.py` - Main Flask application
- `templates/` - HTML templates
- `static/` - Static assets (CSS, JS)
- `.env` - Environment variables
- `requirements.txt` - Python dependencies

## Event Formats

- Push: "{author} pushed to {to_branch} on {timestamp}"
- Pull Request: "{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"
- Merge: "{author} merged branch {from_branch} to {to_branch} on {timestamp}" 