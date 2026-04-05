#!/usr/bin/env python3
"""
Telegram Userbot Sender with YouTube Search
Sends messages from your personal Telegram account using Telethon (MTProto API).
Supports YouTube video search, channel selection, and duplicate prevention via Telegram history.
"""

import os
import sys
import json
import asyncio
import random
import re
from datetime import datetime
from pathlib import Path

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError

# YouTube search using yt-dlp
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

# Skip history check if set
SKIP_HISTORY = os.environ.get('SKIP_HISTORY', '').lower() in ('true', '1', 'yes')


class YouTubeSearcher:
    """Search YouTube for videos using yt-dlp with channel and sorting support."""
    
    SORT_LATEST = 'latest'
    SORT_POPULAR = 'popular'
    SORT_RANDOM = 'random'
    
    def __init__(self):
        if not YT_DLP_AVAILABLE:
            raise ImportError("yt-dlp is not installed. Run: pip install yt-dlp")
    
    def search(self, query: str, max_results: int = 15, sort_by: str = 'random') -> list:
        """Search YouTube for videos."""
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
                            videos.append(self._parse_entry(entry))
            
            return self._sort_videos(videos, sort_by)
            
        except Exception as e:
            print(f"❌ YouTube search error: {e}")
            return []
    
    def search_channel(self, channel_name: str, query: str = '', max_results: int = 15, sort_by: str = 'latest') -> list:
        """Search within a specific YouTube channel."""
        try:
            if query:
                search_query = f"{query} channel:{channel_name}"
            else:
                search_query = f"channel:{channel_name}"
            
            return self.search(search_query, max_results, sort_by)
            
        except Exception as e:
            print(f"❌ Channel search error: {e}")
            return []
    
    def get_channel_videos(self, channel_identifier: str, max_results: int = 15, sort_by: str = 'latest') -> list:
        """Get videos directly from a YouTube channel."""
        try:
            # Determine channel URL
            if 'youtube.com' in channel_identifier or 'youtu.be' in channel_identifier:
                channel_url = channel_identifier.rstrip('/')
                if not channel_url.endswith('/videos'):
                    channel_url += '/videos'
            elif channel_identifier.startswith('@'):
                channel_url = f"https://www.youtube.com/{channel_identifier}/videos"
            elif channel_identifier.startswith('UC') and len(channel_identifier) == 24:
                channel_url = f"https://www.youtube.com/channel/{channel_identifier}/videos"
            else:
                handle = channel_identifier.replace(' ', '').replace('"', '').replace("'", '')
                channel_url = f"https://www.youtube.com/@{handle}/videos"
            
            print(f"   📺 Accessing: {channel_url}")
            
            ydl_opts = {
                'quiet': True,
                'extract_flat': 'in_playlist',
                'no_warnings': True,
                'playlistend': max_results,
                'extractor_args': {'youtube': {'player_client': ['web']}},
            }
            
            videos = []
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    result = ydl.extract_info(channel_url, download=False)
                    
                    if result:
                        entries = []
                        if 'entries' in result:
                            entries = result['entries']
                        elif result.get('_type') == 'playlist':
                            entries = result.get('entries', [])
                        
                        for entry in entries:
                            if entry:
                                if entry.get('_type') == 'playlist':
                                    continue
                                videos.append(self._parse_entry(entry))
                                
                except Exception as e:
                    print(f"⚠️ Direct channel access failed: {e}")
            
            if not videos:
                print(f"   🔄 Trying search fallback for: {channel_identifier}")
                return self.search(f"{channel_identifier}", max_results * 2, sort_by)
            
            return self._sort_videos(videos, sort_by)
            
        except Exception as e:
            print(f"❌ Get channel videos error: {e}")
            return []
    
    def _parse_entry(self, entry: dict) -> dict:
        """Parse a yt-dlp entry into a standardized video dictionary."""
        upload_date = entry.get('upload_date') or entry.get('timestamp')
        
        return {
            'title': entry.get('title', 'Unknown'),
            'link': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id', '')}",
            'duration': self._format_duration(entry.get('duration')),
            'duration_seconds': entry.get('duration', 0),
            'views': entry.get('view_count') or entry.get('view_count_approx', 0),
            'channel': entry.get('channel') or entry.get('uploader', 'Unknown'),
            'channel_url': entry.get('channel_url') or entry.get('uploader_url', ''),
            'id': entry.get('id', ''),
            'upload_date': upload_date,
            'description': (entry.get('description', '') or '')[:200]
        }
    
    def _sort_videos(self, videos: list, sort_by: str) -> list:
        """Sort videos by the specified method."""
        if not videos:
            return videos
        
        if sort_by == self.SORT_LATEST:
            def sort_key(v):
                date = v.get('upload_date')
                if date:
                    if isinstance(date, (int, float)):
                        return -date
                    return str(date)
                return ''
            return sorted(videos, key=sort_key, reverse=True)
        
        elif sort_by == self.SORT_POPULAR:
            def sort_key(v):
                views = v.get('views')
                if views and isinstance(views, (int, float)):
                    return -views
                return 0
            return sorted(videos, key=sort_key)
        
        elif sort_by == self.SORT_RANDOM:
            shuffled = videos.copy()
            random.shuffle(shuffled)
            return shuffled
        
        return videos
    
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
    
    def format_video_message(self, video: dict, template: str = None) -> str:
        """Format a video as a message."""
        if template:
            message = template.format(
                title=video.get('title', 'Unknown'),
                link=video.get('link', ''),
                duration=video.get('duration', 'N/A'),
                views=self._format_views(video.get('views')),
                channel=video.get('channel', 'Unknown'),
                channel_url=video.get('channel_url', '')
            )
        else:
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
        if not views:
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
    """Telegram sender with YouTube integration and duplicate prevention."""
    
    # Regex to extract YouTube video IDs from messages
    YOUTUBE_PATTERNS = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
        r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
    ]
    
    def __init__(self):
        self.client = None
        self.youtube = YouTubeSearcher() if YT_DLP_AVAILABLE else None
        self._sent_video_ids = None
    
    async def initialize_client(self):
        """Initialize the Telegram client."""
        
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
        
        if entity_str.lower() == 'me':
            return 'me'
        
        try:
            entity_id = int(entity_str)
            return await self.client.get_entity(entity_id)
        except ValueError:
            pass
        
        if entity_str.startswith('@'):
            entity_str = entity_str[1:]
        
        try:
            return await self.client.get_entity(entity_str)
        except Exception as e:
            print(f"Error resolving entity: {e}")
            raise
    
    async def get_sent_video_ids(self, entity, limit: int = 100) -> set:
        """
        Get YouTube video IDs from recent messages in the chat.
        This checks what videos have already been sent to prevent duplicates.
        
        Args:
            entity: Telegram entity (chat/user)
            limit: Maximum number of messages to check
            
        Returns:
            Set of YouTube video IDs that have been sent
        """
        if self._sent_video_ids is not None:
            return self._sent_video_ids
        
        if SKIP_HISTORY:
            print("⏭️ Skipping history check (SKIP_HISTORY=true)")
            return set()
        
        print(f"📜 Checking last {limit} messages for sent videos...")
        
        video_ids = set()
        
        try:
            async for message in self.client.iter_messages(entity, limit=limit):
                if message.message:
                    # Extract YouTube video IDs from message text
                    for pattern in self.YOUTUBE_PATTERNS:
                        matches = re.findall(pattern, message.message)
                        video_ids.update(matches)
                    
                    # Also check for bare YouTube links
                    if 'youtube.com' in message.message or 'youtu.be' in message.message:
                        # Find any 11-char video ID
                        ids = re.findall(r'[a-zA-Z0-9_-]{11}', message.message)
                        # Validate they look like video IDs
                        for vid in ids:
                            if len(vid) == 11 and not vid.startswith('UC'):  # UC is channel IDs
                                video_ids.add(vid)
            
            print(f"📊 Found {len(video_ids)} videos already sent in chat history")
            self._sent_video_ids = video_ids
            return video_ids
            
        except Exception as e:
            print(f"⚠️ Error fetching message history: {e}")
            return set()
    
    async def is_video_sent(self, entity, video_id: str) -> bool:
        """Check if a video has already been sent."""
        sent_ids = await self.get_sent_video_ids(entity)
        return video_id in sent_ids
    
    async def send_message(self, entity, message: str, parse_mode: str = 'md'):
        """Send a message to the specified entity."""
        try:
            result = await self.client.send_message(
                entity,
                message,
                parse_mode=parse_mode,
                link_preview=True
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
        
        message_config = self.get_message_config_for_current_time(messages_config)
        
        if not message_config:
            print("⚠️ No message to send at this time.")
            return
        
        # Build message and get video info
        message, video = await self.build_message_with_video(message_config, entity)
        
        if message:
            parse_mode = messages_config.get('parse_mode', 'md')
            await self.send_message(entity, message, parse_mode=parse_mode)
    
    async def build_message_with_video(self, config: dict, entity=None) -> tuple:
        """
        Build a message from configuration with YouTube support.
        Returns (message, video) tuple. Video is None if no YouTube video.
        """
        message_parts = []
        video = None
        
        if config.get('prefix'):
            message_parts.append(config['prefix'])
        
        youtube_config = config.get('youtube_search')
        if youtube_config and self.youtube:
            video = await self._get_unsent_video(youtube_config, entity)
            
            if video:
                template = youtube_config.get('template')
                yt_message = self.youtube.format_video_message(video, template)
                message_parts.append(yt_message)
                print(f"📹 Found: {video.get('title', 'Unknown')}")
                print(f"   Channel: {video.get('channel', 'Unknown')}")
                print(f"   Views: {self.youtube._format_views(video.get('views'))}")
            else:
                query = youtube_config.get('query', '')
                channel = youtube_config.get('channel', '')
                channels = youtube_config.get('channels', [])
                search_desc = f"'{query}'" if query else f"channel '{channel or channels}'"
                message_parts.append(f"obana {search_desc}")
        
        elif config.get('youtube_link'):
            message_parts.append(f"🔗 {config['youtube_link']}")
        
        if config.get('suffix'):
            message_parts.append(config['suffix'])
        
        if not message_parts and config.get('content'):
            message_parts.append(config['content'])
        
        return '\n\n'.join(message_parts), video
    
    async def _get_unsent_video(self, youtube_config: dict, entity=None) -> dict:
        """
        Get a video that hasn't been sent yet.
        Checks Telegram history to avoid duplicates.
        Supports 'channels' array for random channel selection.
        """
        max_results = youtube_config.get('max_results', 15)
        search_max = max(30, max_results * 2)
        
        config_copy = youtube_config.copy()
        config_copy['max_results'] = search_max
        
        videos = []
        selected_channel = None
        
        query = config_copy.get('query', '')
        sort_by = config_copy.get('sort_by', 'latest')
        
        # NEW: Check for 'channels' array (multiple channels - random selection)
        channels_list = config_copy.get('channels', [])
        
        if channels_list:
            # Randomly select one channel from the list
            selected_channel = random.choice(channels_list)
            print(f"   🎲 Random channel selected: {selected_channel} (from {len(channels_list)} channels)")
            
            if query:
                videos = self.youtube.search_channel(selected_channel, query, search_max, sort_by)
            else:
                videos = self.youtube.get_channel_videos(selected_channel, search_max, sort_by)
        
        # Single channel (backward compatible)
        elif config_copy.get('channel'):
            selected_channel = config_copy.get('channel')
            if query:
                videos = self.youtube.search_channel(selected_channel, query, search_max, sort_by)
            else:
                videos = self.youtube.get_channel_videos(selected_channel, search_max, sort_by)
        
        # Regular search (no channel)
        elif query:
            videos = self.youtube.search(query, search_max, sort_by)
        
        if not videos:
            return None
        
        # If we have entity and skip_history is not set, check for duplicates
        if entity and not SKIP_HISTORY:
            sent_ids = await self.get_sent_video_ids(entity)
            
            for video in videos:
                video_id = video.get('id')
                if video_id and video_id not in sent_ids:
                    print(f"   ✨ Found unsent video: {video.get('title', 'Unknown')[:40]}")
                    # Add selected channel info to video dict for reference
                    if selected_channel:
                        video['selected_from_channel'] = selected_channel
                    return video
            
            print(f"   ⚠️ All {len(videos)} videos have already been sent!")
            return None
        
        # No entity or skip_history - return first video
        video = videos[0]
        if selected_channel:
            video['selected_from_channel'] = selected_channel
        return video
    
    async def build_message(self, config: dict) -> str:
        """Build a message from configuration with YouTube support."""
        message, _ = await self.build_message_with_video(config, None)
        return message
    
    def load_messages(self):
        """Load messages configuration from JSON file."""
        try:
            if os.path.exists(MESSAGE_FILE):
                with open(MESSAGE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._get_default_config()
        except Exception as e:
            print(f"❌ Error loading messages: {e}")
            return None
    
    def _get_default_config(self):
        """Get default configuration."""
        return {
            "default_target": TARGET_ENTITY or "me",
            "parse_mode": "md",
            "hourly_messages": [
                {
                    "comment": "Gaming videos",
                    "hours": [0, 6, 12, 18],
                    "prefix": "🎮 **Gaming Update**",
                    "youtube_search": {
                        "channels": ["IGN", "GameTrailers", "PlayStation"],
                        "sort_by": "latest",
                        "max_results": 5,
                        "template": "{link}"
                    }
                },
                {
                    "comment": "Morning motivation",
                    "hours": [7, 8, 9],
                    "prefix": "☀️ **Morning Motivation**",
                    "youtube_search": {
                        "channels": ["MotivationHub", "BeInspired", "Goalcast"],
                        "sort_by": "popular",
                        "max_results": 5,
                        "template": "🎬 {title}\n\n🔗 {link}"
                    }
                }
            ]
        }
    
    def get_message_config_for_current_time(self, config: dict) -> dict:
        """Get message configuration for the current hour."""
        current_hour = datetime.now().hour
        
        hourly_messages = config.get('hourly_messages', [])
        for msg_config in hourly_messages:
            hours = msg_config.get('hours', [])
            if current_hour in hours:
                return msg_config
        
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
    
    print("\n" + "="*60)
    print("YouTube Search Test")
    print("="*60)
    print("\nTest options:")
    print("1. Search by query")
    print("2. Get latest from channel")
    print("3. Search within a channel")
    print("4. Get popular videos")
    print("5. Test random channel selection")
    
    choice = input("\nSelect option (1-5): ")
    
    if choice == '1':
        query = input("Enter search query: ") or "ue5 tutorial"
        print("\nSort by: (1) latest, (2) popular, (3) random")
        sort_choice = input("Select (1-3, default=random): ") or "3"
        sort_map = {'1': 'latest', '2': 'popular', '3': 'random'}
        sort_by = sort_map.get(sort_choice, 'random')
        
        videos = searcher.search(query, max_results=5, sort_by=sort_by)
        
    elif choice == '2':
        channel = input("Enter channel name: ") or "MrBeast"
        videos = searcher.get_channel_videos(channel, max_results=5, sort_by='latest')
        
    elif choice == '3':
        channel = input("Enter channel name: ") or "Unreal Engine"
        query = input("Enter search query (optional): ")
        videos = searcher.search_channel(channel, query, max_results=5, sort_by='latest')
        
    elif choice == '4':
        query = input("Enter search query: ") or "python tutorial"
        videos = searcher.search(query, max_results=5, sort_by='popular')
    
    elif choice == '5':
        channels_input = input("Enter channels (comma-separated): ") or "IGN,GameTrailers,PlayStation"
        channels = [c.strip() for c in channels_input.split(',')]
        selected = random.choice(channels)
        print(f"\n🎲 Randomly selected: {selected} (from {len(channels)} channels)")
        videos = searcher.get_channel_videos(selected, max_results=5, sort_by='latest')
    
    else:
        print("Invalid choice!")
        return
    
    # Display results
    if videos:
        print(f"\n✅ Found {len(videos)} videos:\n")
        for i, video in enumerate(videos, 1):
            print(f"{i}. {video['title']}")
            print(f"   📺 {video['channel']}")
            print(f"   ⏱️ {video['duration']}")
            print(f"   🔗 {video['link']}")
            print()
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