#!/usr/bin/env python3
"""
Test script to verify YouTube search and Telegram sending locally.
Checks Telegram history to prevent duplicates.
"""

import os
import sys
import asyncio
import random
import re

try:
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    import yt_dlp
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Run: pip install telethon yt-dlp")
    sys.exit(1)


class YouTubeTester:
    """YouTube search tester with Telegram history checking."""
    
    YOUTUBE_PATTERNS = [
        r'youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
        r'youtu\.be/([a-zA-Z0-9_-]{11})',
    ]
    
    def __init__(self, client=None, entity=None):
        self.client = client
        self.entity = entity
        self._sent_ids = None
    
    async def get_sent_video_ids(self, limit=50):
        """Get YouTube video IDs from recent Telegram messages."""
        if self._sent_ids is not None:
            return self._sent_ids
        
        if not self.client or not self.entity:
            return set()
        
        print(f"📜 Checking last {limit} messages for sent videos...")
        
        video_ids = set()
        
        try:
            async for message in self.client.iter_messages(self.entity, limit=limit):
                if message.message:
                    for pattern in self.YOUTUBE_PATTERNS:
                        matches = re.findall(pattern, message.message)
                        video_ids.update(matches)
            
            print(f"📊 Found {len(video_ids)} videos already sent")
            self._sent_ids = video_ids
            return video_ids
            
        except Exception as e:
            print(f"⚠️ Error fetching history: {e}")
            return set()
    
    def search(self, query: str, max_results: int = 10, sort_by: str = 'random'):
        """Search YouTube."""
        print(f"\n🔍 Searching: '{query}' (sort: {sort_by})\n")
        
        ydl_opts = {
            'quiet': True,
            'extract_flat': True,
            'default_search': 'ytsearch',
            'max_results': max_results,
            'no_warnings': True,
        }
        
        videos = []
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            search_query = f"ytsearch{max_results}:{query}"
            result = ydl.extract_info(search_query, download=False)
            
            if result and 'entries' in result:
                for entry in result['entries']:
                    if entry:
                        videos.append({
                            'id': entry.get('id', ''),
                            'title': entry.get('title', 'Unknown'),
                            'channel': entry.get('channel') or entry.get('uploader', 'Unknown'),
                            'duration': entry.get('duration', 'N/A'),
                            'views': entry.get('view_count') or 0,
                            'link': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                        })
        
        return self._sort_videos(videos, sort_by)
    
    def get_channel_videos(self, channel: str, max_results: int = 10, sort_by: str = 'latest'):
        """Get videos from a channel."""
        print(f"\n📺 Getting videos from channel: '{channel}'\n")
        
        if 'youtube.com' in channel:
            channel_url = channel.rstrip('/')
            if not channel_url.endswith('/videos'):
                channel_url += '/videos'
        elif channel.startswith('@'):
            channel_url = f"https://www.youtube.com/{channel}/videos"
        else:
            channel_url = f"https://www.youtube.com/@{channel.replace(' ', '')}/videos"
        
        ydl_opts = {
            'quiet': True,
            'extract_flat': 'in_playlist',
            'no_warnings': True,
            'playlistend': max_results,
        }
        
        videos = []
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                result = ydl.extract_info(channel_url, download=False)
                
                if result and 'entries' in result:
                    for entry in result['entries']:
                        if entry and entry.get('_type') != 'playlist':
                            videos.append({
                                'id': entry.get('id', ''),
                                'title': entry.get('title', 'Unknown'),
                                'channel': entry.get('channel') or entry.get('uploader', 'Unknown'),
                                'duration': entry.get('duration', 'N/A'),
                                'views': entry.get('view_count') or 0,
                                'link': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                            })
            except Exception as e:
                print(f"⚠️ Error: {e}")
                return self.search(channel, max_results, sort_by)
        
        return self._sort_videos(videos, sort_by)
    
    async def display_videos(self, videos: list, show_sent_status: bool = True):
        """Display video list with sent status."""
        if not videos:
            print("❌ No videos found!")
            return videos
        
        sent_ids = await self.get_sent_video_ids() if show_sent_status else set()
        
        print(f"\n✅ Found {len(videos)} videos:\n")
        for i, video in enumerate(videos, 1):
            sent_marker = " ✓ SENT" if video.get('id') in sent_ids else " ○ NEW"
            
            print(f"{i}. {video['title'][:50]}")
            print(f"   📺 {video['channel']}")
            if show_sent_status:
                print(f"   📊 {sent_marker}")
            print()
        
        return videos
    
    def _sort_videos(self, videos: list, sort_by: str) -> list:
        if not videos:
            return videos
        
        if sort_by == 'latest':
            return videos
        elif sort_by == 'popular':
            return sorted(videos, key=lambda v: -(v.get('views', 0) or 0))
        elif sort_by == 'random':
            shuffled = videos.copy()
            random.shuffle(shuffled)
            return shuffled
        
        return videos


async def test_telegram_send():
    """Test sending a message with YouTube link to Telegram."""
    
    # Get credentials
    api_id = os.environ.get('TELEGRAM_API_ID') or input("API ID: ")
    api_hash = os.environ.get('TELEGRAM_API_HASH') or input("API Hash: ")
    session_string = os.environ.get('TELEGRAM_SESSION_STRING') or input("Session String: ")
    target = os.environ.get('TELEGRAM_TARGET_ENTITY') or input("Target (me/@username): ")
    
    # Connect to Telegram
    client = TelegramClient(StringSession(session_string), int(api_id), api_hash)
    await client.connect()
    
    if not await client.is_user_authorized():
        print("❌ Session not authorized!")
        return
    
    entity = await client.get_entity(target if target != 'me' else 'me')
    print(f"✅ Connected to: {entity}")
    
    # Initialize tester with Telegram client
    yt = YouTubeTester(client, entity)
    
    print("\n" + "="*50)
    print("YouTube Search Options")
    print("="*50)
    print("1. General search")
    print("2. Latest from channel")
    print("3. Popular videos")
    
    choice = input("\nSelect (1-3): ")
    
    if choice == '1':
        query = input("Search query: ") or "ue5 tutorial"
        videos = yt.search(query, max_results=10, sort_by='popular')
    elif choice == '2':
        channel = input("Channel name: ") or "MrBeast"
        videos = yt.get_channel_videos(channel, max_results=10, sort_by='latest')
    elif choice == '3':
        query = input("Search query: ") or "python tutorial"
        videos = yt.search(query, max_results=10, sort_by='popular')
    else:
        print("Invalid choice!")
        await client.disconnect()
        return
    
    await yt.display_videos(videos)
    
    if not videos:
        await client.disconnect()
        return
    
    # Find unsent video
    sent_ids = await yt.get_sent_video_ids()
    unsent = [v for v in videos if v.get('id') not in sent_ids]
    
    if unsent:
        print(f"\n💡 Suggested (unsent): {unsent[0]['title'][:50]}")
    else:
        print("\n⚠️ All videos have been sent!")
    
    # Select video
    print("\nSelect a video (1-10) or press Enter for suggested:")
    choice = input("> ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(videos):
        video = videos[int(choice) - 1]
    elif unsent:
        video = unsent[0]
    else:
        video = videos[0]
    
    # Check if already sent
    if video.get('id') in sent_ids:
        print(f"\n⚠️ Warning: This video was already sent!")
        confirm = input("Send anyway? (y/n): ")
        if confirm.lower() != 'y':
            print("❌ Cancelled.")
            await client.disconnect()
            return
    
    message = f"🎬 **{video['title']}**\n\n📺 {video['channel']}\n\n🔗 {video['link']}"
    
    print(f"\n📝 Message to send:\n{'-'*50}\n{message}\n{'-'*50}")
    
    confirm = input("\nSend this message? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Cancelled.")
        await client.disconnect()
        return
    
    # Send
    await client.send_message(entity, message, parse_mode='md', link_preview=True)
    print(f"\n✅ Message sent!")
    
    await client.disconnect()


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║        Telegram + YouTube Integration Test Script            ║
║          (Checks Telegram history for duplicates)            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("Options:")
    print("1. Test full Telegram send with YouTube")
    print("2. Quick test: YouTube search only")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ")
    
    if choice == '1':
        asyncio.run(test_telegram_send())
    elif choice == '2':
        yt = YouTubeTester()
        query = input("Search query: ") or "ue5 tutorial"
        videos = yt.search(query, max_results=5)
        print(f"\nFound {len(videos)} videos")
        for v in videos:
            print(f"  - {v['title'][:50]}")
    else:
        print("👋 Bye!")


if __name__ == "__main__":
    main()
