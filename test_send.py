#!/usr/bin/env python3
"""
Test script to verify YouTube search and Telegram sending locally.
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
    def __init__(self):
        pass
    
    def search(self, query: str, max_results: int = 5):
        """Search YouTube and display results."""
        print(f"\n🔍 Searching YouTube for: '{query}'\n")
        
        try:
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
                    for i, entry in enumerate(result['entries'], 1):
                        if entry:
                            video = {
                                'title': entry.get('title', 'Unknown'),
                                'channel': entry.get('channel') or entry.get('uploader', 'Unknown'),
                                'duration': entry.get('duration', 'N/A'),
                                'link': entry.get('url') or f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                                'views': entry.get('view_count', 'N/A')
                            }
                            videos.append(video)
                            
                            print(f"{i}. {video['title']}")
                            print(f"   📺 Channel: {video['channel']}")
                            print(f"   ⏱️ Duration: {self._format_duration(video['duration'])}")
                            print(f"   👁️ Views: {self._format_views(video['views'])}")
                            print(f"   🔗 {video['link']}")
                            print()
            
            return videos
            
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
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
            else:
                return f"{minutes}:{secs:02d}"
        except:
            return str(seconds)
    
    def _format_views(self, views):
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


async def test_telegram_send():
    """Test sending a message with YouTube link to Telegram."""
    
    # Get credentials
    api_id = os.environ.get('TELEGRAM_API_ID') or input("API ID: ")
    api_hash = os.environ.get('TELEGRAM_API_HASH') or input("API Hash: ")
    session_string = os.environ.get('TELEGRAM_SESSION_STRING') or input("Session String: ")
    target = os.environ.get('TELEGRAM_TARGET_ENTITY') or input("Target (me/@username): ")
    
    # Get YouTube query
    query = input("YouTube search query (press Enter for 'ue5 tutorial'): ") or "ue5 tutorial"
    
    # Search YouTube
    yt = YouTubeTester()
    videos = yt.search(query, max_results=5)
    
    if not videos:
        print("❌ No videos found!")
        return
    
    # Select video (first one or let user choose)
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
║                    (Using yt-dlp)                            ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    print("Options:")
    print("1. Test YouTube search only")
    print("2. Test full Telegram send with YouTube")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ")
    
    if choice == '1':
        yt = YouTubeTester()
        query = input("Enter search query: ") or "ue5 tutorial"
        yt.search(query)
    elif choice == '2':
        asyncio.run(test_telegram_send())
    else:
        print("👋 Bye!")


if __name__ == "__main__":
    main()
