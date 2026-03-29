# Telegram YouTube Sender - GitHub Actions

Send **hourly messages with YouTube links** from your personal Telegram account using GitHub Actions. Features channel selection, sorting options, and customizable templates.

## ✨ Features

- 🤖 **Personal Account**: Messages appear from YOUR account, not a bot
- 🔍 **YouTube Integration**: Auto-search and share YouTube videos using yt-dlp
- 📺 **Channel Selection**: Get latest videos from specific channels
- 📊 **Sorting Options**: Sort by latest, popular, or random
- ⏰ **Hourly Sending**: Runs every hour via GitHub Actions cron
- 🔐 **Secure**: All credentials stored as GitHub Secrets
- 🎯 **Flexible Targets**: Send to users, groups, or channels
- 📝 **Custom Templates**: Format messages exactly how you want

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

### Step 4: Customize Messages

Edit `messages.json` and push to GitHub!

---

## 🎬 YouTube Configuration

### Basic Options

| Option | Description | Values |
|--------|-------------|--------|
| `query` | Search query | Any YouTube search term |
| `channel` | Channel name/handle | `"Unreal Engine"`, `"@MrBeast"`, channel URL |
| `sort_by` | Sorting method | `"latest"`, `"popular"`, `"random"` |
| `max_results` | Number of results | `1` to `50` |
| `template` | Message format | See template placeholders |

### Sort Options

| Value | Description | Best For |
|-------|-------------|----------|
| `latest` | Newest videos first | Breaking news, new uploads |
| `popular` | Most views first | Trending content, best tutorials |
| `random` | Random selection | Discovery, variety |

### Template Placeholders

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{title}` | Video title | "UE5 Beginner Tutorial" |
| `{link}` | YouTube URL | "https://youtube.com/watch?v=..." |
| `{channel}` | Channel name | "Unreal Engine" |
| `{channel_url}` | Channel URL | "https://youtube.com/@UnrealEngine" |
| `{duration}` | Video length | "15:30" |
| `{views}` | View count | "1.5M" |

---

## 📝 Configuration Examples

### 1. Latest Video from a Channel

Get the newest video from a specific channel:

```json
{
    "youtube_search": {
        "channel": "Unreal Engine",
        "sort_by": "latest",
        "max_results": 1,
        "template": "🎬 *Latest UE5*\n\n{title}\n\n🔗 {link}"
    }
}
```

### 2. Most Popular Videos

Get the most popular video for a topic:

```json
{
    "youtube_search": {
        "query": "python tutorial 2024",
        "sort_by": "popular",
        "max_results": 10,
        "template": "📚 *Top Python*\n\n🎬 {title}\n📺 {channel}\n👁️ {views}\n\n🔗 {link}"
    }
}
```

### 3. Search Within a Channel

Search for specific content within a channel:

```json
{
    "youtube_search": {
        "channel": "Fireship",
        "query": "javascript",
        "sort_by": "latest",
        "max_results": 5,
        "template": "⚡ *Fireship JS*\n\n🎬 {title}\n\n🔗 {link}"
    }
}
```

### 4. Random Discovery

Discover random videos for a topic:

```json
{
    "youtube_search": {
        "query": "indie game devlog",
        "sort_by": "random",
        "max_results": 20,
        "template": "🎮 *Game Dev*\n\n🎬 {title}\n📺 {channel}\n\n🔗 {link}"
    }
}
```

### 5. Channel by Handle (@username)

Use the @handle format:

```json
{
    "youtube_search": {
        "channel": "@LinusTechTips",
        "sort_by": "latest",
        "max_results": 5,
        "template": "💻 *Tech News*\n\n🎬 {title}\n\n🔗 {link}"
    }
}
```

### 6. Full Hourly Configuration

Complete example with time-based rules:

```json
{
    "default_target": "me",
    "parse_mode": "md",
    "hourly_messages": [
        {
            "hours": [0, 1, 2, 3, 4, 5],
            "prefix": "🌙 *Night Content*",
            "youtube_search": {
                "channel": "Lofi Girl",
                "sort_by": "latest",
                "template": "🎵 {title}\n\n🔗 {link}"
            }
        },
        {
            "hours": [6, 7, 8, 9, 10, 11],
            "prefix": "☀️ *Morning*",
            "youtube_search": {
                "query": "morning motivation",
                "sort_by": "popular",
                "template": "🎯 {title}\n📺 {channel}\n\n🔗 {link}"
            }
        },
        {
            "hours": [12, 13, 14, 15, 16, 17],
            "prefix": "📚 *Learning*",
            "youtube_search": {
                "channel": "Unreal Engine",
                "query": "tutorial",
                "sort_by": "latest",
                "template": "🎮 {title}\n⏱️ {duration}\n\n🔗 {link}"
            }
        },
        {
            "hours": [18, 19, 20, 21, 22, 23],
            "prefix": "🌆 *Evening*",
            "youtube_search": {
                "query": "relaxing music",
                "sort_by": "random",
                "template": "🎶 {title}\n📺 {channel}\n\n🔗 {link}"
            }
        }
    ]
}
```

---

## ⏰ Schedule Configuration

**Default: Every hour**
```yaml
schedule:
  - cron: '0 * * * *'
```

**Custom schedules:**
```yaml
# Every 2 hours
- cron: '0 */2 * * *'

# Every 30 minutes
- cron: '*/30 * * * *'

# Specific times
- cron: '0 9,12,18,21 * * *'
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

### Manual GitHub Trigger
1. Actions → Select workflow → Run workflow
2. Enter custom YouTube query
3. Run

---

## ⚠️ Node.js Fix

The workflow includes:

```yaml
env:
  FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true
```

This fixes the Node.js 20 deprecation warning.

---

## 📁 Project Structure

```
telegram-userbot-github-actions/
├── .github/workflows/
│   ├── telegram-sender.yml
│   └── telegram-sender-simple.yml
├── telegram_sender.py
├── setup.py
├── test_send.py
├── messages.json
├── requirements.txt
└── README.md
```

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| "yt-dlp not installed" | `pip install yt-dlp` |
| "No results found" | Check channel name/URL |
| "Session not authorized" | Re-run `--setup` |
| Workflow not running | Check Actions tab for errors |

---

## 📜 License

MIT License - Use responsibly!
