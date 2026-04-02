#!/usr/bin/env python3
"""
Video History Manager
Tracks sent YouTube videos to prevent duplicates.
Uses a JSON file for storage, compatible with GitHub Actions artifacts.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Set


class VideoHistory:
    """Manages history of sent YouTube videos to prevent duplicates."""
    
    DEFAULT_HISTORY_FILE = 'sent_videos_history.json'
    MAX_HISTORY_SIZE = 1000  # Keep last 1000 videos to prevent file from growing too large
    
    def __init__(self, history_file: str = None):
        """
        Initialize history manager.
        
        Args:
            history_file: Path to the history JSON file
        """
        self.history_file = history_file or os.environ.get('HISTORY_FILE', self.DEFAULT_HISTORY_FILE)
        self._history: Dict = self._load_history()
    
    def _load_history(self) -> Dict:
        """Load history from JSON file."""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"📂 Loaded {len(data.get('videos', []))} videos from history")
                    return data
        except Exception as e:
            print(f"⚠️ Error loading history: {e}")
        
        # Return default structure
        return {
            'videos': [],  # List of sent video records
            'stats': {
                'total_sent': 0,
                'first_sent': None,
                'last_sent': None
            }
        }
    
    def save(self) -> bool:
        """Save history to JSON file."""
        try:
            # Trim history if too large
            if len(self._history.get('videos', [])) > self.MAX_HISTORY_SIZE:
                self._history['videos'] = self._history['videos'][-self.MAX_HISTORY_SIZE:]
            
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self._history, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Saved history ({len(self._history.get('videos', []))} videos)")
            return True
        except Exception as e:
            print(f"❌ Error saving history: {e}")
            return False
    
    def get_sent_video_ids(self) -> Set[str]:
        """Get set of all sent video IDs."""
        return {v.get('id') for v in self._history.get('videos', []) if v.get('id')}
    
    def is_sent(self, video_id: str) -> bool:
        """
        Check if a video has already been sent.
        
        Args:
            video_id: YouTube video ID
            
        Returns:
            True if video was already sent, False otherwise
        """
        return video_id in self.get_sent_video_ids()
    
    def mark_sent(self, video: Dict, target: str = None) -> bool:
        """
        Mark a video as sent.
        
        Args:
            video: Video dictionary with id, title, link, etc.
            target: Target entity where video was sent
            
        Returns:
            True if successfully marked, False if already sent
        """
        video_id = video.get('id')
        
        if not video_id:
            print("⚠️ Cannot mark video as sent: missing video ID")
            return False
        
        # Check if already sent
        if self.is_sent(video_id):
            print(f"⚠️ Video {video_id} already in history")
            return False
        
        # Add to history
        record = {
            'id': video_id,
            'title': video.get('title', 'Unknown'),
            'channel': video.get('channel', 'Unknown'),
            'link': video.get('link', ''),
            'sent_at': datetime.now().isoformat(),
            'target': target
        }
        
        self._history.setdefault('videos', []).append(record)
        
        # Update stats
        stats = self._history.setdefault('stats', {})
        stats['total_sent'] = stats.get('total_sent', 0) + 1
        stats['last_sent'] = datetime.now().isoformat()
        if not stats.get('first_sent'):
            stats['first_sent'] = datetime.now().isoformat()
        
        print(f"✅ Marked as sent: {video.get('title', 'Unknown')[:50]}")
        return True
    
    def get_next_unsent(self, videos: List[Dict]) -> Optional[Dict]:
        """
        Get the next video from a list that hasn't been sent yet.
        
        Args:
            videos: List of video dictionaries
            
        Returns:
            First unsent video, or None if all have been sent
        """
        sent_ids = self.get_sent_video_ids()
        
        for video in videos:
            video_id = video.get('id')
            if video_id and video_id not in sent_ids:
                return video
        
        return None
    
    def get_recent_sent(self, count: int = 10) -> List[Dict]:
        """Get recently sent videos."""
        videos = self._history.get('videos', [])
        return videos[-count:][::-1]  # Return last N videos in reverse order (newest first)
    
    def get_stats(self) -> Dict:
        """Get history statistics."""
        return self._history.get('stats', {})
    
    def clear_history(self) -> bool:
        """Clear all history."""
        try:
            self._history = {
                'videos': [],
                'stats': {
                    'total_sent': 0,
                    'first_sent': None,
                    'last_sent': None
                }
            }
            self.save()
            print("🗑️ History cleared")
            return True
        except Exception as e:
            print(f"❌ Error clearing history: {e}")
            return False
    
    def remove_video(self, video_id: str) -> bool:
        """Remove a specific video from history."""
        try:
            videos = self._history.get('videos', [])
            original_count = len(videos)
            
            self._history['videos'] = [v for v in videos if v.get('id') != video_id]
            
            if len(self._history['videos']) < original_count:
                self.save()
                print(f"🗑️ Removed video {video_id} from history")
                return True
            else:
                print(f"⚠️ Video {video_id} not found in history")
                return False
        except Exception as e:
            print(f"❌ Error removing video: {e}")
            return False


def print_history_summary(history: VideoHistory, count: int = 10):
    """Print a summary of the video history."""
    print("\n" + "="*60)
    print("📊 VIDEO HISTORY SUMMARY")
    print("="*60)
    
    stats = history.get_stats()
    print(f"\n📈 Statistics:")
    print(f"   Total sent: {stats.get('total_sent', 0)}")
    if stats.get('first_sent'):
        print(f"   First sent: {stats['first_sent']}")
    if stats.get('last_sent'):
        print(f"   Last sent: {stats['last_sent']}")
    
    recent = history.get_recent_sent(count)
    if recent:
        print(f"\n📝 Recently sent ({len(recent)}):")
        for i, v in enumerate(recent, 1):
            print(f"   {i}. [{v.get('id')}] {v.get('title', 'Unknown')[:40]}")
            print(f"      Channel: {v.get('channel', 'Unknown')}")
            print(f"      Sent: {v.get('sent_at', 'Unknown')}")
    else:
        print("\n📝 No videos in history yet")
    
    print("="*60)


if __name__ == "__main__":
    import sys
    
    history = VideoHistory()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == '--show':
            count = int(sys.argv[2]) if len(sys.argv) > 2 else 10
            print_history_summary(history, count)
        
        elif cmd == '--clear':
            confirm = input("Are you sure you want to clear all history? (yes/no): ")
            if confirm.lower() == 'yes':
                history.clear_history()
        
        elif cmd == '--stats':
            stats = history.get_stats()
            print(json.dumps(stats, indent=2))
        
        else:
            print(f"Unknown command: {cmd}")
            print("Usage: python history_manager.py [--show | --clear | --stats]")
    else:
        print_history_summary(history)
