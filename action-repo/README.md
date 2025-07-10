# Github Action Repository

This repository is configured to send webhook events to our webhook receiver for the following Github actions:
- Push events
- Pull Request events
- Merge events

## Webhook Configuration

1. Go to repository Settings > Webhooks
2. Add webhook:
   - Payload URL: `http://your-domain:5000/webhook`
   - Content Type: `application/json`
   - Events to trigger webhook:
     - Push events
     - Pull requests
     - Active: ✓

## Testing Webhook Events

### Push Event
```bash
# Create and push changes
git checkout -b feature/test
echo "test" > test.txt
git add test.txt
git commit -m "test commit"
git push origin feature/test
```

Expected format: "{author} pushed to {to_branch} on {timestamp}"

### Pull Request Event
1. Create a new branch
2. Make changes and push
3. Create Pull Request via Github UI

Expected format: "{author} submitted a pull request from {from_branch} to {to_branch} on {timestamp}"

### Merge Event
1. Review and approve PR
2. Merge PR via Github UI

Expected format: "{author} merged branch {from_branch} to {to_branch} on {timestamp}"

## Sample Files

This repository contains sample files to test webhook events:
- `test.txt` - Use for push events
- `feature.txt` - Use for pull request testing
- `README.md` - Documentation updates 