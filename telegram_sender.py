#!/usr/bin/env python3
"""
Telegram Userbot Sender
Sends messages from your personal Telegram account using Telethon (MTProto API).
Supports session persistence for GitHub Actions integration.
"""

import os
import sys
import json
import base64
import asyncio
from datetime import datetime
from pathlib import Path

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.tl.types import InputPeerUser, InputPeerChat, InputPeerChannel


# Configuration from environment variables
API_ID = os.environ.get('TELEGRAM_API_ID')
API_HASH = os.environ.get('TELEGRAM_API_HASH')
PHONE_NUMBER = os.environ.get('TELEGRAM_PHONE')
SESSION_STRING = os.environ.get('TELEGRAM_SESSION_STRING')

# Target configuration
TARGET_ENTITY = os.environ.get('TELEGRAM_TARGET_ENTITY')  # Username, phone, or chat ID
MESSAGE_FILE = os.environ.get('MESSAGE_FILE', 'messages.json')
SESSION_FILE = 'telegram_session.session'

# For storing session as artifact
SESSION_ARTIFACT_DIR = Path('/tmp/session_artifact')


class TelegramSender:
    def __init__(self):
        self.client = None
        
    async def initialize_client(self):
        """Initialize the Telegram client with session persistence."""
        
        if not API_ID or not API_HASH:
            raise ValueError("TELEGRAM_API_ID and TELEGRAM_API_HASH must be set!")
        
        # Convert API_ID to integer
        api_id = int(API_ID)
        
        # Check if we have a session string (for GitHub Actions)
        if SESSION_STRING:
            print("📌 Using session string from environment...")
            self.client = TelegramClient(
                StringSession(SESSION_STRING),
                api_id,
                API_HASH
            )
        else:
            # Use file-based session
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
        if not await self.client.is_user_authorized():
            return False
        return True
    
    async def send_login_code(self):
        """Send login code to the phone number (for initial setup)."""
        if not PHONE_NUMBER:
            raise ValueError("TELEGRAM_PHONE must be set for initial login!")
        
        await self.client.send_code_request(PHONE_NUMBER)
        print(f"✅ Verification code sent to {PHONE_NUMBER}")
        print("Please set TELEGRAM_CODE environment variable with the received code.")
        return True
    
    async def complete_login(self, code: str, password: str = None):
        """Complete the login process with the verification code."""
        try:
            await self.client.sign_in(PHONE_NUMBER, code)
            print("✅ Successfully signed in!")
            return True
        except SessionPasswordNeededError:
            if password:
                await self.client.sign_in(password=password)
                print("✅ Successfully signed in with 2FA password!")
                return True
            else:
                print("⚠️ 2FA password required. Set TELEGRAM_2FA_PASSWORD environment variable.")
                return False
        except PhoneCodeInvalidError:
            print("❌ Invalid verification code!")
            return False
    
    async def get_session_string(self):
        """Export the session as a string for GitHub Actions secrets."""
        return StringSession.save(self.client.session)
    
    async def resolve_entity(self, entity_str: str):
        """Resolve entity string to a Telegram entity."""
        entity_str = entity_str.strip()
        
        # Try to parse as integer (user/chat ID)
        try:
            entity_id = int(entity_str)
            return await self.client.get_entity(entity_id)
        except ValueError:
            pass
        
        # Try as username (with or without @)
        if entity_str.startswith('@'):
            entity_str = entity_str[1:]
        
        # Try to get entity by username
        try:
            return await self.client.get_entity(entity_str)
        except Exception as e:
            print(f"Error resolving entity: {e}")
            raise
    
    async def send_message(self, entity, message: str, parse_mode: str = None):
        """Send a message to the specified entity."""
        try:
            result = await self.client.send_message(
                entity,
                message,
                parse_mode=parse_mode
            )
            print(f"✅ Message sent successfully!")
            print(f"   Message ID: {result.id}")
            return result
        except Exception as e:
            print(f"❌ Failed to send message: {e}")
            raise
    
    async def send_scheduled_messages(self):
        """Send messages based on the schedule configuration."""
        
        # Load messages from JSON file
        messages_config = self.load_messages()
        
        if not messages_config:
            print("⚠️ No messages configured!")
            return
        
        # Get target entity
        target = TARGET_ENTITY or messages_config.get('default_target')
        if not target:
            raise ValueError("No target entity specified! Set TELEGRAM_TARGET_ENTITY or default_target in messages.json")
        
        entity = await self.resolve_entity(target)
        print(f"🎯 Target: {entity}")
        
        # Determine which message to send based on time
        message = self.get_message_for_current_time(messages_config)
        
        if message:
            parse_mode = messages_config.get('parse_mode', 'md')
            await self.send_message(entity, message, parse_mode=parse_mode)
        else:
            print("⚠️ No message to send at this time.")
    
    def load_messages(self):
        """Load messages configuration from JSON file."""
        try:
            if os.path.exists(MESSAGE_FILE):
                with open(MESSAGE_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # Default configuration
                default_config = {
                    "default_target": TARGET_ENTITY,
                    "parse_mode": "md",
                    "messages": [
                        {
                            "time": "00:00",
                            "content": "🌅 Good morning! This is your scheduled message."
                        },
                        {
                            "time": "06:00",
                            "content": "☀️ Good day! Time for your morning reminder."
                        },
                        {
                            "time": "12:00",
                            "content": "🌤️ Afternoon check-in! How's your day going?"
                        },
                        {
                            "time": "18:00",
                            "content": "🌙 Evening update! Time to wind down."
                        }
                    ]
                }
                print(f"⚠️ Message file not found. Using default configuration.")
                return default_config
        except Exception as e:
            print(f"❌ Error loading messages: {e}")
            return None
    
    def get_message_for_current_time(self, config):
        """Get the appropriate message based on current time."""
        messages = config.get('messages', [])
        current_hour = datetime.now().hour
        
        # Find the closest scheduled message
        for msg in messages:
            time_str = msg.get('time', '00:00')
            try:
                msg_hour, msg_minute = map(int, time_str.split(':'))
                # Match within 1 hour window
                if abs(current_hour - msg_hour) <= 1:
                    return msg.get('content')
            except ValueError:
                continue
        
        # Fallback: cycle through messages based on hour
        if messages:
            index = (current_hour // 6) % len(messages)
            return messages[index].get('content')
        
        return None
    
    async def close(self):
        """Close the client connection."""
        if self.client:
            await self.client.disconnect()


async def initial_setup():
    """
    Run this locally to set up the session for the first time.
    This will generate a session string for GitHub Actions.
    """
    print("🚀 Starting initial setup...")
    
    sender = TelegramSender()
    
    try:
        api_id = int(API_ID)
        
        # Use StringSession for easy export
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
        
        # Export session string
        session_string = StringSession.save(client.session)
        print("\n" + "="*60)
        print("🎉 Setup complete! Here's your session string:")
        print("="*60)
        print(f"\n{session_string}\n")
        print("="*60)
        print("\n📋 Copy the session string above and add it as a")
        print("   GitHub Secret named 'TELEGRAM_SESSION_STRING'")
        print("="*60)
        
        await client.disconnect()
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        raise


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
    if len(sys.argv) > 1 and sys.argv[1] == '--setup':
        asyncio.run(initial_setup())
    else:
        asyncio.run(main())
