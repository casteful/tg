# Telegram YouTube Sender - GitHub Actions

Send **hourly messages with YouTube links** from your personal Telegram account using GitHub Actions. Features channel selection, sorting options, and **duplicate prevention via Telegram history**.

## ✨ Features

- 🤖 **Personal Account**: Messages appear from YOUR account, not a bot
- 🔍 **YouTube Integration**: Auto-search and share YouTube videos using yt-dlp
- 📺 **Channel Selection**: Get latest videos from specific channels
- 📊 **Sorting Options**: Sort by latest, popular, or random
- 🚫 **Smart Duplicate Prevention**: Checks Telegram history - no extra files needed!
- ⏰ **Hourly Sending**: Runs every hour via GitHub Actions cron
- 🔐 **Secure**: All credentials stored as GitHub Secrets

---

## 🚫 Duplicate Prevention

The app **checks your Telegram chat history** to find videos already sent - no extra files or commits needed!

### How It Works

1. **Fetch History**: Gets last 100 messages from target chat
2. **Extract Video IDs**: Finds YouTube video IDs from message text
3. **Skip Duplicates**: Automatically picks an unsent video
4. **No Files Needed**: History is checked directly from Telegram

### Benefits

- ✅ No repository commits needed
- ✅ No merge conflicts
- ✅ Checks what was *actually* sent
- ✅ Works across all workflow runs

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

### Step 4: Customize and Push

Edit `messages.json` and push to GitHub!

---

## 🎬 YouTube Configuration

### Basic Options

| Option | Description | Values |
|--------|-------------|--------|
| `query` | Search query | Any YouTube search term |
| `channel` | Channel name/handle | `"MrBeast"`, `"@UnrealEngine"` |
| `sort_by` | Sorting method | `"latest"`, `"popular"`, `"random"` |
| `max_results` | Number of results | `1` to `50` |
| `template` | Message format | See placeholders below |

### Template Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{title}` | Video title | "UE5 Tutorial" |
| `{link}` | YouTube URL | "https://youtube.com/watch?v=..." |
| `{channel}` | Channel name | "Unreal Engine" |
| `{duration}` | Video length | "15:30" |
| `{views}` | View count | "1.5M" |

---

## 📝 Configuration Examples

### Get Latest from Channel

```json
{
    "youtube_search": {
        "channel": "MrBeast",
        "sort_by": "latest",
        "max_results": 20,
        "template": "🎬 {title}\n\n🔗 {link}"
    }
}
```

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
                "sort_by": "latest"
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

## ⚙️ Manual Trigger Options

| Option | Description |
|--------|-------------|
| `youtube_query` | Custom search query |
| `channel_name` | Specific channel |
| `sort_by` | latest/popular/random |
| `skip_history` | Send even if already sent |

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

---

## 📁 Project Structure

```
telegram-userbot-github-actions/
├── .github/workflows/
│   └── telegram-sender.yml    # Single workflow
├── telegram_sender.py          # Main script
├── setup.py                    # Session setup
├── test_send.py                # Local testing
├── messages.json               # Message config
└── requirements.txt            # Dependencies
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "All videos have been sent" | New videos will be sent when available |
| Channel not found | Use exact channel handle (@name) |
| Session not authorized | Re-run `--setup` |

---

## 📜 License

MIT License - Use responsibly!
