#!/usr/bin/env python3
"""
Quick test script to send a test message locally.
"""

import os
import sys
import asyncio

try:
    from telethon import TelegramClient
    from telethon.sessions import StringSession
except ImportError:
    print("❌ Telethon not installed. Run: pip install telethon")
    sys.exit(1)


async def send_test_message():
    # Get credentials from environment or prompt
    api_id = os.environ.get('TELEGRAM_API_ID') or input("API ID: ")
    api_hash = os.environ.get('TELEGRAM_API_HASH') or input("API Hash: ")
    session_string = os.environ.get('TELEGRAM_SESSION_STRING') or input("Session String: ")
    target = os.environ.get('TELEGRAM_TARGET_ENTITY') or input("Target (me/@username/chat_id): ")
    message = input("Message (press Enter for default): ") or "🤖 Test message from GitHub Actions setup!"
    
    try:
        api_id = int(api_id)
    except ValueError:
        print("❌ API ID must be a number!")
        return
    
    print(f"\n🔌 Connecting...")
    
    try:
        client = TelegramClient(StringSession(session_string), api_id, api_hash)
        await client.connect()
        
        if not await client.is_user_authorized():
            print("❌ Session is not valid. Please regenerate.")
            return
        
        print(f"📤 Sending message to {target}...")
        
        entity = await client.get_entity(target if target != 'me' else 'me')
        await client.send_message(entity, message, parse_mode='md')
        
        print(f"✅ Message sent successfully to {entity}!")
        
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(send_test_message())
