# Telegram Userbot - GitHub Actions Sender

Send scheduled messages from **your personal Telegram account** using GitHub Actions. This project uses Telethon (MTProto API) to automate your personal account instead of a bot account.

## ✨ Features

- 🤖 **Personal Account**: Messages appear from YOUR account, not a bot
- ⏰ **Scheduled Sending**: 4 times daily via GitHub Actions cron
- 💾 **Session Persistence**: Session survives between GitHub Actions runs
- 🔐 **Secure**: All credentials stored as GitHub Secrets
- 🎯 **Flexible Targets**: Send to users, groups, or channels
- 📝 **Customizable Messages**: JSON-based message configuration
- 🔄 **Manual Trigger**: Test messages via workflow_dispatch

## 📋 Prerequisites

1. **Telegram Account**: Your personal account with phone number
2. **Telegram API Credentials**: Get from [my.telegram.org](https://my.telegram.org)
3. **GitHub Repository**: To host the workflow

## 🚀 Quick Start

### Step 1: Get Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Navigate to "API development tools"
4. Create a new application (if not exists)
5. Copy your **API ID** and **API Hash**

### Step 2: Run Initial Setup (Required!)

**Run this locally first** to generate your session string:

```bash
# Clone or download this project
cd telegram-userbot-github-actions

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"
export TELEGRAM_PHONE="+1234567890"  # Your phone with country code

# Run setup
python telegram_sender.py --setup
```

The script will:
1. Send a verification code to your Telegram
2. Ask you to enter the code
3. Ask for 2FA password (if enabled)
4. **Output a session string** - COPY THIS!

### Step 3: Configure GitHub Secrets

In your GitHub repository, go to **Settings → Secrets and variables → Actions** and add:

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `TELEGRAM_API_ID` | Your API ID from my.telegram.org | `12345` |
| `TELEGRAM_API_HASH` | Your API Hash | `a1b2c3d4e5f6...` |
| `TELEGRAM_SESSION_STRING` | Session string from setup | `1AZWarz...` |
| `TELEGRAM_TARGET_ENTITY` | Where to send messages | `@username` or `me` |

#### Target Entity Options:
- `me` - Send to "Saved Messages" (yourself)
- `@username` - Send to a user by username
- `+1234567890` - Send to a phone number
- `123456789` - Send to a chat/channel ID
- `group_name` - Send to a group

### Step 4: Customize Your Messages

Edit `messages.json` to set your messages:

```json
{
    "default_target": "me",
    "parse_mode": "md",
    "messages": [
        {
            "time": "00:00",
            "content": "🌅 *Good Morning!*\n\nYour midnight reminder."
        },
        {
            "time": "06:00",
            "content": "☀️ *Morning!*\n\nStart your day right!"
        },
        {
            "time": "12:00",
            "content": "🌤️ *Afternoon!*\n\nHalfway there!"
        },
        {
            "time": "18:00",
            "content": "🌙 *Evening!*\n\nTime to wrap up."
        }
    ]
}
```

### Step 5: Push to GitHub and Enable Actions

1. Push the code to your GitHub repository
2. Go to **Actions** tab
3. Enable GitHub Actions if prompted
4. The workflow will run automatically at scheduled times

## 📅 Schedule Configuration

The default schedule runs **4 times a day** (every 6 hours):

```yaml
schedule:
  - cron: '0 */6 * * *'  # 00:00, 06:00, 12:00, 18:00 UTC
```

### Custom Schedule Examples:

```yaml
# Every hour
- cron: '0 * * * *'

# Twice daily (8 AM and 8 PM UTC)
- cron: '0 8,20 * * *'

# Every 4 hours
- cron: '0 */4 * * *'

# Specific times: 9 AM and 6 PM UTC
- cron: '0 9,18 * * *'
```

## 🧪 Testing

### Manual Trigger via GitHub UI

1. Go to **Actions** tab
2. Select "Telegram Scheduled Sender"
3. Click "Run workflow"
4. Optionally enter a custom message
5. Click "Run workflow"

### Local Testing

```bash
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"
export TELEGRAM_SESSION_STRING="your_session_string"
export TELEGRAM_TARGET_ENTITY="me"

python telegram_sender.py
```

## 🔒 Security Best Practices

1. **Never commit secrets** to the repository
2. **Use GitHub Secrets** for all sensitive data
3. **Limit repository access** - secrets are visible to collaborators
4. **Enable 2FA** on your Telegram account
5. **Regenerate session** if compromised: re-run `--setup`

## ⚠️ Important Notes

### Telegram Terms of Service

Automating personal accounts may violate Telegram's ToS if used for spam. This tool is intended for:
- ✅ Personal reminders
- ✅ Self-notifications
- ✅ Content you own
- ❌ Spam or unsolicited messages
- ❌ Bulk messaging

### Rate Limits

Telegram has rate limits for userbots:
- ~30 messages/second to different chats
- ~5 messages/second to the same chat

For 4 messages per day, you're well within limits.

### Session Persistence

Two methods are provided:

1. **Session String (Recommended)**: Stored as GitHub Secret, works reliably
2. **Artifacts**: Session file uploaded/downloaded between runs (backup method)

The workflow tries the artifact method first, falls back to session string.

## 📁 Project Structure

```
telegram-userbot-github-actions/
├── .github/
│   └── workflows/
│       └── telegram-sender.yml    # GitHub Actions workflow
├── telegram_sender.py              # Main Python script
├── messages.json                   # Message configuration
├── requirements.txt                # Python dependencies
└── README.md                       # This file
```

## 🐛 Troubleshooting

### "Session not authorized"
- Re-run `python telegram_sender.py --setup` locally
- Update `TELEGRAM_SESSION_STRING` secret

### "API ID invalid"
- Check credentials at my.telegram.org
- Ensure `TELEGRAM_API_ID` is a number (no quotes in secret)

### "Entity not found"
- Check `TELEGRAM_TARGET_ENTITY` format
- For users: try `@username` or phone number
- For channels: use channel ID with `-100` prefix

### "2FA password required"
- Run `--setup` locally with your 2FA password
- Session string includes authentication

### Workflow not running
- Check Actions tab for errors
- Verify all secrets are set correctly
- Ensure workflow is enabled

## 📜 License

MIT License - Use responsibly!

## 🤝 Contributing

Feel free to open issues or submit PRs for improvements!

---

**Made with ❤️ for personal automation**
