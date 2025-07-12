# GitHub Webhook Action Repository

This repository demonstrates GitHub Actions integration with webhooks. It automatically sends webhook events to a registered endpoint for the following GitHub actions:
- Push events
- Pull Request events (open, reopen, close)
- Merge events (when a pull request is merged)

## Setup Instructions

1. **Repository Secrets**
   You need to configure two repository secrets in your GitHub repository settings:
   - `WEBHOOK_URL`: The URL of your webhook endpoint (e.g., `https://your-domain.com/webhook`)
   - `WEBHOOK_SECRET`: A secret token that matches the one configured in your webhook receiver

   To add these secrets:
   1. Go to your repository's Settings
   2. Click on "Secrets and variables" → "Actio
   3. Click "New repository secret"
   4. Add both `WEBHOOK_URL` and `WEBHOOK_SECRET`

2. **Webhook Events**
   The workflow will automatically trigger and send webhook events for:
   - Any push to any branch
   - Opening a pull request
   - Reopening a pull request
   - Closing a pull request (including merges)

3. **Event Format**
   The webhook sends events in the following format:

   For Push events:
   ```json
   {
     "ref": "refs/heads/branch-name",
     "after": "commit-sha",
     "repository": {
       "full_name": "owner/repo"
     },
     "sender": {
       "login": "username"
     }
   }
   ```

   For Pull Request events:
   ```json
   {
     "action": "opened|closed",
     "pull_request": {
       "id": 123,
       "merged": false,
       "head": {
         "ref": "feature-branch"
       },
       "base": {
         "ref": "main"
       }
     },
     "repository": {
       "full_name": "owner/repo"
     },
     "sender": {
       "login": "username"
     }
   }
   ```

4. **Security**
   - The webhook includes a SHA1 HMAC signature in the `X-Hub-Signature` header
   - The signature is calculated using the webhook secret
   - The receiver should validate this signature to ensure the request is authentic

## Testing

To test the webhook:

1. Make a push to any branch:
   ```bash
   git push origin your-branch
   ```

2. Create a pull request:
   - Create a new branch
   - Make changes
   - Push the branch
   - Open a pull request on GitHub

3. Merge a pull request:
   - Go to the pull request on GitHub
   - Click "Merge pull request"

You can verify the events in your webhook receiver's logs or UI.

## Troubleshooting

1. **Webhook Not Receiving Events**
   - Check if the `WEBHOOK_URL` secret is correct
   - Verify the URL is accessible
   - Check if the webhook receiver is running

2. **Invalid Signature Errors**
   - Verify the `WEBHOOK_SECRET` matches in both repositories
   - Check if the payload is being properly signed

3. **Action Workflow Failures**
   - Check the Actions tab in GitHub for error logs
   - Verify all required secrets are configured
   - Ensure the webhook URL is responding 