# Telegram YouTube Sender - GitHub Actions

Send **hourly messages with YouTube links** from your personal Telegram account using GitHub Actions. This project combines Telethon (MTProto API) with yt-dlp to deliver customized video recommendations automatically.

## ✨ Features

- 🤖 **Personal Account**: Messages appear from YOUR account, not a bot
- 🔍 **YouTube Integration**: Auto-search and share YouTube videos using yt-dlp
- ⏰ **Hourly Sending**: Runs every hour via GitHub Actions cron
- 🎲 **Random Videos**: Gets random videos from search results for variety
- 📅 **Time-based Queries**: Different search queries for different times of day
- 🔐 **Secure**: All credentials stored as GitHub Secrets
- 🎯 **Flexible Targets**: Send to users, groups, or channels
- 📝 **Custom Templates**: Format messages exactly how you want
- 🔄 **Manual Trigger**: Test via workflow_dispatch with custom queries

## 📋 Prerequisites

1. **Telegram Account**: Your personal account with phone number
2. **Telegram API Credentials**: Get from [my.telegram.org](https://my.telegram.org)
3. **GitHub Repository**: To host the workflow

## 🚀 Quick Start

### Step 1: Get Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Navigate to "API development tools"
4. Create a new application
5. Copy your **API ID** and **API Hash**

### Step 2: Run Initial Setup

Run this locally to generate your session string:

```bash
# Install dependencies
pip install telethon yt-dlp

# Set environment variables
export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"

# Run setup
python telegram_sender.py --setup
```

The script will output a **session string** - copy it!

### Step 3: Configure GitHub Secrets

In your GitHub repository: **Settings → Secrets and variables → Actions**

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `TELEGRAM_API_ID` | Your API ID | `12345` |
| `TELEGRAM_API_HASH` | Your API Hash | `a1b2c3d4...` |
| `TELEGRAM_SESSION_STRING` | Session string from setup | `1AZWarz...` |
| `TELEGRAM_TARGET_ENTITY` | Where to send | `me` or `@username` |

### Step 4: Customize Messages

Edit `messages.json` to configure your hourly YouTube searches:

```json
{
    "default_target": "me",
    "parse_mode": "md",
    "hourly_messages": [
        {
            "hours": [0, 1, 2, 3, 4, 5],
            "prefix": "🌙 *Late Night Vibes*",
            "youtube_search": {
                "query": "lofi hip hop radio night",
                "random": true,
                "template": "🎵 *{title}*\n\n📺 {channel}\n🔗 {link}"
            }
        },
        {
            "hours": [6, 7, 8, 9, 10, 11],
            "prefix": "☀️ *Good Morning!*",
            "youtube_search": {
                "query": "morning motivation music",
                "random": true
            }
        }
    ]
}
```

### Step 5: Push to GitHub

1. Push the code to your repository
2. Go to **Actions** tab
3. Enable GitHub Actions if prompted
4. Messages will be sent every hour automatically!

## 🎬 YouTube Search Configuration

### Message Template Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{title}` | Video title | "Lofi Hip Hop Radio" |
| `{link}` | YouTube URL | "https://youtube.com/watch?v=..." |
| `{channel}` | Channel name | "Lofi Girl" |
| `{duration}` | Video length | "3:45:22" |
| `{views}` | View count | "10M views" |

### Example Configurations

**Simple music recommendation:**
```json
{
    "hours": [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23],
    "youtube_search": {
        "query": "lofi beats",
        "random": true,
        "template": "🎵 {title}\n\n🔗 {link}"
    }
}
```

**UE5 Tutorials:**
```json
{
    "youtube_search": {
        "query": "ue5 tutorial beginner",
        "random": true,
        "max_results": 20,
        "template": "🎮 **UE5 Tutorial**\n\n🎬 {title}\n📺 {channel}\n⏱️ {duration}\n\n🔗 {link}"
    }
}
```

**Time-based categories:**
```json
{
    "hourly_messages": [
        {
            "hours": [6, 7, 8],
            "youtube_search": { "query": "morning workout music" }
        },
        {
            "hours": [9, 10, 11, 12, 13, 14, 15, 16, 17],
            "youtube_search": { "query": "focus music study" }
        },
        {
            "hours": [18, 19, 20, 21, 22, 23, 0, 1, 2, 3, 4, 5],
            "youtube_search": { "query": "relaxing evening music" }
        }
    ]
}
```

**Learning content:**
```json
{
    "youtube_search": {
        "query": "python programming tutorial",
        "random": true,
        "template": "📚 *Daily Learning*\n\n🎬 {title}\n📺 {channel}\n⏱️ {duration}\n\n🔗 {link}"
    }
}
```

## ⏰ Schedule Configuration

**Default: Every hour**
```yaml
schedule:
  - cron: '0 * * * *'  # Every hour at minute 0
```

**Custom schedules:**
```yaml
# Every 2 hours
- cron: '0 */2 * * *'

# Every 30 minutes
- cron: '*/30 * * * *'

# Every 6 hours
- cron: '0 */6 * * *'
```

## 🧪 Testing

### Test YouTube Search Locally
```bash
python telegram_sender.py --test-youtube
```

### Test Full Message Send
```bash
python test_send.py
```

### Manual Trigger on GitHub
1. Go to **Actions** tab
2. Select the workflow
3. Click "Run workflow"
4. Optionally enter a custom YouTube query
5. Click "Run workflow"

## ⚠️ Node.js Deprecation Fix

This project includes the fix for the Node.js 20 deprecation warning:

```yaml
env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
```

This forces GitHub Actions to use Node.js 24, avoiding the deprecation warning.

## 📦 Dependencies

This project uses **yt-dlp** for YouTube searches, which is:
- ✅ Actively maintained
- ✅ No API key required
- ✅ Works reliably without rate limiting issues
- ✅ Provides video metadata (title, duration, views, etc.)

## ⚠️ Important Notes

### Telegram Rate Limits

For hourly messages (24 per day), you're well within Telegram's limits:
- ~30 messages/second to different chats
- ~5 messages/second to same chat

### Telegram ToS

Use responsibly for:
- ✅ Personal reminders
- ✅ Self-notifications
- ✅ Your own content
- ❌ Spam or bulk messaging

## 📁 Project Structure

```
telegram-userbot-github-actions/
├── .github/
│   └── workflows/
│       ├── telegram-sender.yml        # Main workflow
│       └── telegram-sender-simple.yml # Simplified workflow
├── telegram_sender.py                  # Main script with YouTube support
├── setup.py                            # Session setup helper
├── test_send.py                        # Local testing script
├── messages.json                       # Message configuration
├── requirements.txt                    # Dependencies
└── README.md                           # Documentation
```

## 🐛 Troubleshooting

### "yt-dlp not installed"
```bash
pip install yt-dlp
```

### "No YouTube results found"
- Check your search query
- Try simpler keywords
- Check your internet connection

### "Session not authorized"
- Re-run `python telegram_sender.py --setup`
- Update `TELEGRAM_SESSION_STRING` secret

### Workflow not running
- Check Actions tab for errors
- Verify all 4 secrets are set
- Ensure workflow file is in `.github/workflows/`

## 📜 License

MIT License - Use responsibly!

---

**Made with ❤️ for personal automation**
