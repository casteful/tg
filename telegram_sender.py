#!/usr/bin/env python3
"""
Telegram Userbot Sender with YouTube Search
Sends messages from your personal Telegram account using Telethon (MTProto API).
Supports YouTube video search and link inclusion using yt-dlp.
"""

import os
import sys
import json
import asyncio
import random
from datetime import datetime
from pathlib import Path

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

# YouTube search using yt-dlp (more reliable)
try:
    import yt_dlp
    YT_DLP_AVAILABLE = True
except ImportError:
    YT_DLP_AVAILABLE = False
    print("⚠️ yt-dlp not installed. YouTube features disabled.")


# Configuration from environment variables
API_ID = os.environ.get('TELEGRAM_API_ID')
API_HASH = os.environ.get('TELEGRAM_API_HASH')
PHONE_NUMBER = os.environ.get('TELEGRAM_PHONE')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')

# Target configuration
TARGET_ENTITY = os.environ.get('TELEGRAM_TARGET_ENTITY')
MESSAGE_FILE = os.environ.get('MESSAGE_FILE', 'messages.json')
SESSION_FILE = 'telegram_session.session'


class YouTubeSearcher:
    """Search YouTube for videos using yt-dlp."""
    
    def __init__(self):
        if not YT_DLP_AVAILABLE:
            raise ImportError("yt-dlp is not installed. Run: pip install yt-dlp")
    
    def search(self, query: str, max_results: int = 10) -> list:
        """
        Search YouTube for videos.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of video dictionaries with title, link, duration, views, etc.
        """
        try:
            ydl_opts = {
                'quiet': True,
                'extract_flat': True,
                'default_search': 'ytsearch',
                'max_results': max_results,
                'no_warnings': True,
                'extract_descriptions': False,
            }
            
            videos = []
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                search_query = f"ytsearch{max_results}:{query}"
                result = ydl.extract_info(search_query, download=False)
                
                if result and 'entries' in result:
                    for entry in result['entries']:
                        if entry:
                            videos.append({
                                'title': entry.get('title', 'Unknown'),
                                'link': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                                'duration': self._format_duration(entry.get('duration')),
                                'views': entry.get('view_count', 'N/A'),
                                'channel': entry.get('channel') or entry.get('uploader', 'Unknown'),
                                'id': entry.get('id', ''),
                                'description': entry.get('description', '')[:200] if entry.get('description') else ''
                            })
            
            return videos
            
        except Exception as e:
            print(f"❌ YouTube search error: {e}")
            return []
    
    def _format_duration(self, seconds):
        """Format duration in seconds to HH:MM:SS or MM:SS."""
        if not seconds:
            return 'N/A'
        
        try:
            seconds = int(seconds)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            
            if hours > 0:
                return f"{hours}:{minutes:02d}:{secs:02d}"
            else:
                return f"{minutes}:{secs:02d}"
        except:
            return str(seconds)
    
    def get_random_video(self, query: str, max_results: int = 15) -> dict:
        """Get a single random video from search results."""
        videos = self.search(query, max_results=max_results)
        if videos:
            return random.choice(videos)
        return None
    
    def get_top_video(self, query: str) -> dict:
        """Get the top video from search results."""
        videos = self.search(query, max_results=1)
        if videos:
            return videos[0]
        return None
    
    def format_video_message(self, video: dict, template: str = None) -> str:
        """
        Format a video as a message.
        
        Args:
            video: Video dictionary
            template: Optional custom template with placeholders
            
        Returns:
            Formatted message string
        """
        if template:
            # Replace placeholders
            message = template.format(
                title=video.get('title', 'Unknown'),
                link=video.get('link', ''),
                duration=video.get('duration', 'N/A'),
                views=self._format_views(video.get('views')),
                channel=video.get('channel', 'Unknown')
            )
        else:
            # Default format
            views_str = self._format_views(video.get('views'))
            message = f"🎬 **{video.get('title', 'Unknown')}**\n\n"
            message += f"📺 Channel: {video.get('channel', 'Unknown')}\n"
            message += f"⏱️ Duration: {video.get('duration', 'N/A')}\n"
            if views_str and views_str != 'N/A':
                message += f"👁️ Views: {views_str}\n"
            message += f"\n🔗 {video.get('link', '')}"
        
        return message
    
    def _format_views(self, views):
        """Format view count."""
        if not views or views == 'N/A':
            return 'N/A'
        
        try:
            views = int(views)
            if views >= 1_000_000:
                return f"{views / 1_000_000:.1f}M"
            elif views >= 1_000:
                return f"{views / 1_000:.1f}K"
            else:
                return str(views)
        except:
            return str(views)


class TelegramSender:
    def __init__(self):
        self.client = None
        self.youtube = YouTubeSearcher() if YT_DLP_AVAILABLE else None
        
    async def initialize_client(self):
        """Initialize the Telegram client with session persistence."""
        
        if not API_ID or not API_HASH:
            raise ValueError("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set!")
        
        api_id = int(API_ID)
        
        if SESSION_STRING:
            print("📌 Using session string from environment...")
            self.client = TelegramClient(
                StringSession(SESSION_STRING),
                api_id,
                API_HASH
            )
        else:
            print("📁 Using file-based session...")
            self.client = TelegramClient(
                SESSION_FILE,
                api_id,
                API_HASH
            )
        
        await self.client.connect()
        return self.client
    
    async def check_authorized(self):
        """Check if the client is authorized."""
        return await self.client.is_user_authorized()
    
    async def resolve_entity(self, entity_str: str):
        """Resolve entity string to a Telegram entity."""
        entity_str = entity_str.strip()
        
        # Special case for 'me'
        if entity_str.lower() == 'me':
            return 'me'
        
        # Try to parse as integer (user/chat ID)
        try:
            entity_id = int(entity_str)
            return await self.client.get_entity(entity_id)
        except ValueError:
            pass
        
        # Try as username (with or without @)
        if entity_str.startswith('@'):
            entity_str = entity_str[1:]
        
        try:
            return await self.client.get_entity(entity_str)
        except Exception as e:
            print(f"Error resolving entity: {e}")
            raise
    
    async def send_message(self, entity, message: str, parse_mode: str = 'md'):
        """Send a message to the specified entity."""
        try:
            result = await self.client.send_message(
                entity,
                message,
                parse_mode=parse_mode,
                link_preview=True  # Enable link preview for YouTube
            )
            print(f"✅ Message sent successfully!")
            print(f"   Message ID: {result.id}")
            return result
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            raise
    
    async def send_scheduled_messages(self):
        """Send messages based on the schedule configuration."""
        
        messages_config = self.load_messages()
        
        if not messages_config:
            print("⚠️ No messages configured!")
            return
        
        target = TARGET_ENTITY or messages_config.get('default_target')
        if not target:
            raise ValueError("No target entity specified!")
        
        entity = await self.resolve_entity(target)
        print(f"🎯 Target: {entity}")
        
        # Get message configuration for current time
        message_config = self.get_message_config_for_current_time(messages_config)
        
        if not message_config:
            print("⚠️ No message to send at this time.")
            return
        
        # Build the message
        message = await self.build_message(message_config)
        
        if message:
            parse_mode = messages_config.get('parse_mode', 'md')
            await self.send_message(entity, message, parse_mode=parse_mode)
    
    async def build_message(self, config: dict) -> str:
        """
        Build a message from configuration.
        Supports YouTube search integration.
        """
        message_parts = []
        
        # Add prefix text
        if config.get('prefix'):
            message_parts.append(config['prefix'])
        
        # Handle YouTube search
        youtube_config = config.get('youtube_search')
        if youtube_config and self.youtube:
            query = youtube_config.get('query', '')
            template = youtube_config.get('template')
            random_video = youtube_config.get('random', True)
            max_results = youtube_config.get('max_results', 15)
            
            print(f"🔍 Searching YouTube for: {query}")
            
            if random_video:
                video = self.youtube.get_random_video(query, max_results=max_results)
            else:
                video = self.youtube.get_top_video(query)
            
            if video:
                yt_message = self.youtube.format_video_message(video, template)
                message_parts.append(yt_message)
                print(f"📹 Found: {video.get('title', 'Unknown')}")
            else:
                message_parts.append(f"⚠️ No YouTube results found for: {query}")
        
        # Add custom link if provided
        elif config.get('youtube_link'):
            message_parts.append(f"🔗 {config['youtube_link']}")
        
        # Add suffix text
        if config.get('suffix'):
            message_parts.append(config['suffix'])
        
        # Add main content if no special processing
        if not message_parts and config.get('content'):
            message_parts.append(config['content'])
        
        return '\n\n'.join(message_parts)
    
    def load_messages(self):
        """Load messages configuration from JSON file."""
        try:
            if os.path.exists(MESSAGE_FILE):
                with open(MESSAGE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                default_config = {
                    "default_target": TARGET_ENTITY or "me",
                    "parse_mode": "md",
                    "hourly_messages": [
                        {
                            "hours": [0, 1, 2, 3, 4, 5],
                            "youtube_search": {
                                "query": "relaxing music",
                                "random": True,
                                "template": "🎵 **Night Time Relaxation**\n\n🎬 {title}\n📺 {channel}\n⏱️ {duration}\n\n🔗 {link}"
                            }
                        },
                        {
                            "hours": [6, 7, 8, 9, 10, 11],
                            "youtube_search": {
                                "query": "morning motivation",
                                "random": True,
                                "template": "☀️ **Morning Motivation**\n\n🎬 {title}\n📺 {channel}\n\n🔗 {link}"
                            }
                        },
                        {
                            "hours": [12, 13, 14, 15, 16, 17],
                            "youtube_search": {
                                "query": "productive music",
                                "random": True,
                                "template": "🎯 **Productivity Boost**\n\n🎬 {title}\n⏱️ {duration}\n\n🔗 {link}"
                            }
                        },
                        {
                            "hours": [18, 19, 20, 21, 22, 23],
                            "youtube_search": {
                                "query": "evening chill music",
                                "random": True,
                                "template": "🌙 **Evening Chill**\n\n🎬 {title}\n📺 {channel}\n\n🔗 {link}"
                            }
                        }
                    ]
                }
                print("⚠️ Message file not found. Using default configuration.")
                return default_config
        except Exception as e:
            print(f"❌ Error loading messages: {e}")
            return None
    
    def get_message_config_for_current_time(self, config: dict) -> dict:
        """Get message configuration for the current hour."""
        current_hour = datetime.now().hour
        
        # Check hourly messages first
        hourly_messages = config.get('hourly_messages', [])
        for msg_config in hourly_messages:
            hours = msg_config.get('hours', [])
            if current_hour in hours:
                return msg_config
        
        # Fallback to time-based messages
        messages = config.get('messages', [])
        for msg in messages:
            time_str = msg.get('time', '')
            if time_str:
                try:
                    msg_hour, msg_minute = map(int, time_str.split(':'))
                    if abs(current_hour - msg_hour) <= 1:
                        return msg
                except ValueError:
                    continue
        
        # If nothing matched, use first hourly message or first regular message
        if hourly_messages:
            return hourly_messages[0]
        if messages:
            return messages[0]
        
        return None
    
    async def close(self):
        """Close the client connection."""
        if self.client:
            await self.client.disconnect()


async def initial_setup():
    """Run this locally to set up the session for the first time."""
    print("🚀 Starting initial setup...")
    
    try:
        api_id = int(API_ID)
        
        client = TelegramClient(StringSession(), api_id, API_HASH)
        await client.connect()
        
        if not await client.is_user_authorized():
            if not PHONE_NUMBER:
                PHONE = input("Enter your phone number (with country code): ")
            else:
                PHONE = PHONE_NUMBER
            
            await client.send_code_request(PHONE)
            print(f"✅ Code sent to {PHONE}")
            
            code = input("Enter the verification code: ")
            
            try:
                await client.sign_in(PHONE, code)
            except SessionPasswordNeededError:
                password = input("Enter your 2FA password: ")
                await client.sign_in(password=password)
        
        session_string = StringSession.save(client.session)
        print("\n" + "="*60)
        print("🎉 Setup complete! Here's your session string:")
        print("="*60)
        print(f"\n{session_string}\n")
        print("="*60)
        
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        raise


async def test_youtube_search():
    """Test YouTube search functionality."""
    if not YT_DLP_AVAILABLE:
        print("❌ yt-dlp not installed!")
        return
    
    searcher = YouTubeSearcher()
    
    queries = ["python tutorial", "ue5 tutorial", "lofi beats"]
    query = input("Enter search query (or press Enter for random): ") or random.choice(queries)
    
    print(f"\n🔍 Testing YouTube search with: {query}")
    videos = searcher.search(query, max_results=5)
    
    if videos:
        print(f"\n✅ Found {len(videos)} videos:\n")
        for i, video in enumerate(videos, 1):
            print(f"{i}. {video['title']}")
            print(f"   📺 {video['channel']}")
            print(f"   ⏱️ {video['duration']}")
            print(f"   🔗 {video['link']}")
            print()
        
        # Test random video
        print("\n--- Random Video Message Format ---\n")
        random_video = searcher.get_random_video(query)
        print(searcher.format_video_message(random_video))
    else:
        print("❌ No results found")


async def main():
    """Main function for sending messages."""
    sender = TelegramSender()
    
    try:
        await sender.initialize_client()
        
        if not await sender.check_authorized():
            print("❌ Not authorized! Run initial setup first.")
            sys.exit(1)
        
        await sender.send_scheduled_messages()
        
    finally:
        await sender.close()


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == '--setup':
            asyncio.run(initial_setup())
        elif sys.argv[1] == '--test-youtube':
            asyncio.run(test_youtube_search())
        else:
            print("Unknown option. Use --setup or --test-youtube")
    else:
        asyncio.run(main())
