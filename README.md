# Telegram YouTube Sender - GitHub Actions

Send **hourly messages with YouTube links** from your personal Telegram account using GitHub Actions. Features channel selection, sorting options, **duplicate prevention**, and customizable templates.

## ✨ Features

- 🤖 **Personal Account**: Messages appear from YOUR account, not a bot
- 🔍 **YouTube Integration**: Auto-search and share YouTube videos using yt-dlp
- 📺 **Channel Selection**: Get latest videos from specific channels
- 📊 **Sorting Options**: Sort by latest, popular, or random
- 🚫 **Duplicate Prevention**: Never send the same video twice!
- ⏰ **Hourly Sending**: Runs every hour via GitHub Actions cron
- 🔐 **Secure**: All credentials stored as GitHub Secrets
- 🎯 **Flexible Targets**: Send to users, groups, or channels

---

## 🚫 Duplicate Prevention

The app automatically tracks sent videos and won't send the same one twice!

### How It Works

1. **History Tracking**: Every sent video is recorded in `sent_videos_history.json`
2. **Artifact Persistence**: GitHub Actions saves history between runs
3. **Smart Selection**: Automatically finds the next unsent video
4. **Fallback**: If all videos have been sent, shows a warning

### View History Locally

```bash
python history_manager.py --show
```

### Clear History

```bash
python history_manager.py --clear
```

---

## 📋 Prerequisites

1. **Telegram Account**: Your personal account with phone number
2. **Telegram API Credentials**: Get from [my.telegram.org](https://my.telegram.org)
3. **GitHub Repository**: To host the workflow

---

## 🚀 Quick Start

### Step 1: Get Telegram API Credentials

1. Go to [my.telegram.org](https://my.telegram.org)
2. Log in with your phone number
3. Navigate to "API development tools"
4. Create a new application
5. Copy your **API ID** and **API Hash**

### Step 2: Run Initial Setup

```bash
pip install telethon yt-dlp

export TELEGRAM_API_ID="your_api_id"
export TELEGRAM_API_HASH="your_api_hash"

python telegram_sender.py --setup
```

### Step 3: Configure GitHub Secrets

In your GitHub repository: **Settings → Secrets and variables → Actions**

| Secret Name | Example |
|-------------|---------|
| `TELEGRAM_API_ID` | `12345` |
| `TELEGRAM_API_HASH` | `a1b2c3d4...` |
| `TELEGRAM_SESSION_STRING` | `1AZWarz...` |
| `TELEGRAM_TARGET_ENTITY` | `me` or `@username` |

### Step 4: Push to GitHub

Push the code and enable GitHub Actions!

---

## 🎬 YouTube Configuration

### Basic Options

| Option | Description | Values |
|--------|-------------|--------|
| `query` | Search query | Any YouTube search term |
| `channel` | Channel name/handle | `"MrBeast"`, `"@UnrealEngine"` |
| `sort_by` | Sorting method | `"latest"`, `"popular"`, `"random"` |
| `max_results` | Number of results | `1` to `50` |
| `template` | Message format | See template placeholders |

### Template Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{title}` | Video title | "UE5 Beginner Tutorial" |
| `{link}` | YouTube URL | "https://youtube.com/watch?v=..." |
| `{channel}` | Channel name | "Unreal Engine" |
| `{duration}` | Video length | "15:30" |
| `{views}` | View count | "1.5M" |

---

## 📝 Configuration Examples

### Get Latest from Channel (Never Duplicates!)

```json
{
    "youtube_search": {
        "channel": "MrBeast",
        "sort_by": "latest",
        "max_results": 10,
        "template": "🎬 {title}\n\n🔗 {link}"
    }
}
```

**How it works:**
- Gets the 10 latest videos from MrBeast
- Checks history to find videos not yet sent
- Sends the first unsent video
- Marks it as sent for next time

### Full Hourly Configuration

```json
{
    "default_target": "me",
    "parse_mode": "md",
    "hourly_messages": [
        {
            "hours": [0, 1, 2, 3, 4, 5],
            "youtube_search": {
                "channel": "Lofi Girl",
                "sort_by": "latest",
                "template": "🎵 {title}\n\n🔗 {link}"
            }
        },
        {
            "hours": [6, 7, 8, 9, 10, 11],
            "youtube_search": {
                "query": "morning motivation",
                "sort_by": "popular"
            }
        }
    ]
}
```

---

## 🧪 Testing

### Test YouTube Search
```bash
python telegram_sender.py --test-youtube
```

### Test Full Send
```bash
python test_send.py
```

### View History
```bash
python history_manager.py --show
```

---

## 📁 Project Structure

```
telegram-userbot-github-actions/
├── .github/workflows/
│   └── telegram-sender.yml        # Single workflow (schedule + manual)
├── telegram_sender.py              # Main script
├── history_manager.py              # Duplicate prevention
├── setup.py                        # Session setup
├── test_send.py                    # Local testing
├── messages.json                   # Message config
├── sent_videos_history.json        # Sent video history (auto-generated)
└── requirements.txt                # Dependencies
```

---

## ⚙️ Manual Trigger Options

When manually triggering on GitHub:

| Option | Description |
|--------|-------------|
| `youtube_query` | Custom search query |
| `channel_name` | Specific channel |
| `sort_by` | latest/popular/random |
| `skip_history` | Send even if already sent |

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "All videos have been sent" | Clear history or add new content |
| "No history found" | Normal for first run |
| Channel not found | Use exact channel handle (@name) |

---

## 📜 License

MIT License - Use responsibly!
