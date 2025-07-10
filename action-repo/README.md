# Action Repository

This is a test repository configured to send webhook events to our webhook receiver application. It's used to demonstrate GitHub webhook functionality for:
- Push events
- Pull Request events
- Merge events

## Purpose

This repository is configured to send webhook events to our webhook receiver application. When any of the following actions occur in this repository:
- Pushing code
- Creating pull requests
- Merging branches

A webhook notification will be sent to our webhook receiver, which will then:
1. Process the event
2. Store it in MongoDB
3. Display it in the UI

## Testing Webhook Events

To test different events:

1. Push Event:
```bash
# Make some changes
git add .
git commit -m "test: trigger push event"
git push origin main
```

2. Pull Request Event:
```bash
# Create a new branch
git checkout -b feature/test
# Make changes
git add .
git commit -m "feat: test pull request"
git push origin feature/test
# Create PR through GitHub interface
```

3. Merge Event:
```bash
# Through GitHub interface, merge the PR
# Or locally:
git checkout main
git merge feature/test
git push origin main
``` 