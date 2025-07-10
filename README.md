# GitHub Events Monitor

This application monitors GitHub repository events (Push, Pull Request, and Merge) using webhooks and displays them in a real-time web interface.

## Features

- Captures GitHub webhook events (Push, Pull Request, and Merge)
- Stores events in MongoDB
- Real-time UI updates (15-second polling)
- Clean and minimal event display

## Setup Instructions

1. Clone the repository:
```bash
git clone <your-webhook-repo-url>
cd webhook-repo
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up MongoDB:
- Install MongoDB if not already installed
- Create a `.env` file with your MongoDB connection string:
```
MONGO_URI=mongodb://localhost:27017/
```

4. Run the application:
```bash
python app.py
```

5. Configure GitHub Webhook:
- Go to your action-repo settings
- Navigate to Webhooks
- Add webhook:
  - Payload URL: `http://your-domain:5000/webhook`
  - Content type: `application/json`
  - Select events: `Pushes`, `Pull requests`
  - Enable SSL verification if using HTTPS

## Usage

1. The application will run on `http://localhost:5000`
2. The UI automatically updates every 15 seconds
3. Events are displayed in chronological order with the following format:
   - Push: "{author} pushed to {to_branch} on {timestamp}"
   - Pull Request: "{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"
   - Merge: "{author} merged branch {from_branch} to {to_branch} on {timestamp}"

## Project Structure

```
webhook-repo/
├── app.py              # Flask application
├── requirements.txt    # Python dependencies
├── templates/         
│   └── index.html     # Frontend UI template
└── .env               # Environment variables
```

## Notes

- Make sure your webhook endpoint is publicly accessible
- The application uses UTC timestamps
- Events are stored in MongoDB for persistence
- The UI displays the 10 most recent events 