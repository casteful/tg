#!/usr/bin/env python3
"""
Test script to verify YouTube search and Telegram sending locally.
Supports channel selection and sorting options.
"""

import os
import sys
import asyncio
import random

try:
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    import yt_dlp
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("Run: pip install telethon yt-dlp")
    sys.exit(1)


class YouTubeTester:
    """YouTube search tester with channel and sorting support."""
    
    SORT_LATEST = 'latest'
    SORT_POPULAR = 'popular'
    SORT_RANDOM = 'random'
    
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
                            'title': entry.get('title', 'Unknown'),
                            'channel': entry.get('channel') or entry.get('uploader', 'Unknown'),
                            'duration': entry.get('duration', 'N/A'),
                            'views': entry.get('view_count') or 0,
                            'link': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                        })
        
        return self._sort_videos(videos, sort_by)
    
    def get_channel_videos(self, channel: str, max_results: int = 10, sort_by: str = 'latest'):
        """Get videos from a channel."""
        print(f"\n📺 Getting videos from channel: '{channel}' (sort: {sort_by})\n")
        
        # Determine channel URL - append /videos to get the videos tab
        if 'youtube.com' in channel:
            channel_url = channel.rstrip('/')
            if not channel_url.endswith('/videos'):
                channel_url += '/videos'
        elif channel.startswith('@'):
            channel_url = f"https://www.youtube.com/{channel}/videos"
        else:
            channel_url = f"https://www.youtube.com/@{channel.replace(' ', '')}/videos"
        
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
                
                if result and 'entries' in result:
                    for entry in result['entries']:
                        if entry and entry.get('_type') != 'playlist':
                            videos.append({
                                'title': entry.get('title', 'Unknown'),
                                'channel': entry.get('channel') or entry.get('uploader', 'Unknown'),
                                'duration': entry.get('duration', 'N/A'),
                                'views': entry.get('view_count') or 0,
                                'link': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                            })
            except Exception as e:
                print(f"⚠️ Direct access failed: {e}")
        
        # Fallback to search if no videos found
        if not videos:
            print(f"   🔄 Trying search fallback...")
            return self.search(channel, max_results * 2, sort_by)
        
        return self._sort_videos(videos, sort_by)
    
    def search_in_channel(self, channel: str, query: str, max_results: int = 10, sort_by: str = 'latest'):
        """Search within a channel."""
        print(f"\n🔍 Searching '{query}' in channel: '{channel}' (sort: {sort_by})\n")
        return self.search(f"{query} channel:{channel}", max_results, sort_by)
    
    def _sort_videos(self, videos: list, sort_by: str) -> list:
        """Sort videos."""
        if not videos:
            return videos
        
        if sort_by == self.SORT_LATEST:
            # Already sorted by recency from yt-dlp
            return videos
        elif sort_by == self.SORT_POPULAR:
            return sorted(videos, key=lambda v: -(v.get('views', 0) or 0))
        elif sort_by == self.SORT_RANDOM:
            shuffled = videos.copy()
            random.shuffle(shuffled)
            return shuffled
        
        return videos
    
    def display_videos(self, videos: list):
        """Display video list."""
        if not videos:
            print("❌ No videos found!")
            return
        
        print(f"✅ Found {len(videos)} videos:\n")
        for i, video in enumerate(videos, 1):
            views_str = self._format_views(video.get('views'))
            print(f"{i}. {video['title']}")
            print(f"   📺 {video['channel']}")
            print(f"   ⏱️ {self._format_duration(video['duration'])}")
            if views_str and views_str != 'N/A':
                print(f"   👁️ {views_str}")
            print(f"   🔗 {video['link']}")
            print()
    
    def _format_duration(self, seconds):
        if not seconds:
            return 'N/A'
        try:
            seconds = int(seconds)
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            if hours > 0:
                return f"{hours}:{minutes:02d}:{secs:02d}"
            return f"{minutes}:{secs:02d}"
        except:
            return str(seconds)
    
    def _format_views(self, views):
        if not views:
            return 'N/A'
        try:
            views = int(views)
            if views >= 1_000_000:
                return f"{views / 1_000_000:.1f}M"
            elif views >= 1_000:
                return f"{views / 1_000:.1f}K"
            return str(views)
        except:
            return str(views)


async def test_telegram_send():
    """Test sending a message with YouTube link to Telegram."""
    
    # Get credentials
    api_id = os.environ.get('TELEGRAM_API_ID') or input("API ID: ")
    api_hash = os.environ.get('TELEGRAM_API_HASH') or input("API Hash: ")
    session_string = os.environ.get('TELEGRAM_SESSION_STRING') or input("Session String: ")
    target = os.environ.get('TELEGRAM_TARGET_ENTITY') or input("Target (me/@username): ")
    
    # YouTube options
    print("\n" + "="*50)
    print("YouTube Search Options")
    print("="*50)
    print("1. General search")
    print("2. Latest from channel")
    print("3. Search within channel")
    
    choice = input("\nSelect (1-3): ")
    
    yt = YouTubeTester()
    videos = []
    
    if choice == '1':
        query = input("Search query: ") or "ue5 tutorial"
        print("\nSort: (1) latest, (2) popular, (3) random")
        sort_choice = input("Select (default=2): ") or "2"
        sort_map = {'1': 'latest', '2': 'popular', '3': 'random'}
        videos = yt.search(query, max_results=5, sort_by=sort_map.get(sort_choice, 'popular'))
        
    elif choice == '2':
        channel = input("Channel name: ") or "Unreal Engine"
        videos = yt.get_channel_videos(channel, max_results=5, sort_by='latest')
        
    elif choice == '3':
        channel = input("Channel name: ") or "Unreal Engine"
        query = input("Search query: ") or "tutorial"
        videos = yt.search_in_channel(channel, query, max_results=5, sort_by='latest')
    
    else:
        print("Invalid choice!")
        return
    
    yt.display_videos(videos)
    
    if not videos:
        return
    
    # Select video
    print("\nSelect a video (1-5) or press Enter for first:")
    choice = input("> ")
    
    if choice.isdigit() and 1 <= int(choice) <= len(videos):
        video = videos[int(choice) - 1]
    else:
        video = videos[0]
    
    message = f"🎬 **{video['title']}**\n\n📺 {video['channel']}\n⏱️ {yt._format_duration(video['duration'])}\n\n🔗 {video['link']}"
    
    print(f"\n📝 Message to send:\n{'-'*50}\n{message}\n{'-'*50}")
    
    confirm = input("\nSend this message? (y/n): ")
    if confirm.lower() != 'y':
        print("❌ Cancelled.")
        return
    
    # Send via Telegram
    try:
        api_id_int = int(api_id)
        client = TelegramClient(StringSession(session_string), api_id_int, api_hash)
        await client.connect()
        
        if not await client.is_user_authorized():
            print("❌ Session not authorized!")
            return
        
        entity = await client.get_entity(target if target != 'me' else 'me')
        await client.send_message(entity, message, parse_mode='md', link_preview=True)
        
        print(f"\n✅ Message sent to {entity}!")
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║        Telegram + YouTube Integration Test Script            ║
║           (Channel Selection & Sorting Support)              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("Options:")
    print("1. Test YouTube search only")
    print("2. Test full Telegram send with YouTube")
    print("3. Quick test: Latest from channel")
    print("4. Quick test: Popular videos")
    print("5. Exit")
    
    choice = input("\nSelect option (1-5): ")
    
    yt = YouTubeTester()
    
    if choice == '1':
        print("\n--- YouTube Search Test ---")
        query = input("Enter search query: ") or "ue5 tutorial"
        print("\nSort: (1) latest, (2) popular, (3) random")
        sort_choice = input("Select (default=3): ") or "3"
        sort_map = {'1': 'latest', '2': 'popular', '3': 'random'}
        videos = yt.search(query, max_results=5, sort_by=sort_map.get(sort_choice, 'random'))
        yt.display_videos(videos)
        
    elif choice == '2':
        asyncio.run(test_telegram_send())
        
    elif choice == '3':
        channel = input("Channel name (default=Unreal Engine): ") or "Unreal Engine"
        videos = yt.get_channel_videos(channel, max_results=5, sort_by='latest')
        yt.display_videos(videos)
        
    elif choice == '4':
        query = input("Search query (default=python tutorial): ") or "python tutorial"
        videos = yt.search(query, max_results=5, sort_by='popular')
        yt.display_videos(videos)
        
    else:
        print("👋 Bye!")


if __name__ == "__main__":
    main()
