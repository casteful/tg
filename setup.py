#!/usr/bin/env python3
"""
Setup helper script for generating Telegram session string.
Run this locally to create your session for GitHub Actions.
"""

import os
import sys
import asyncio

# Check if telethon is installed
try:
    from telethon import TelegramClient
    from telethon.sessions import StringSession
    from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
except ImportError:
    print("❌ Telethon not installed. Run: pip install telethon")
    sys.exit(1)


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════════╗
║     Telegram Userbot Session Generator for GitHub Actions    ║
╚══════════════════════════════════════════════════════════════╝
    """)


def get_input(prompt, default=None, password=False):
    """Get user input with optional default value."""
    if default:
        prompt = f"{prompt} [{default}]: "
    else:
        prompt = f"{prompt}: "
    
    if password:
        import getpass
        value = getpass.getpass(prompt)
    else:
        value = input(prompt)
    
    return value if value else default


async def generate_session():
    print_banner()
    
    # Get API credentials
    print("📱 First, you need your Telegram API credentials.")
    print("   Get them from: https://my.telegram.org/apps\n")
    
    api_id = get_input("Enter your API ID")
    api_hash = get_input("Enter your API Hash")
    phone = get_input("Enter your phone number (with country code, e.g., +1234567890)")
    
    if not all([api_id, api_hash, phone]):
        print("❌ All fields are required!")
        return
    
    try:
        api_id = int(api_id)
    except ValueError:
        print("❌ API ID must be a number!")
        return
    
    print("\n🔌 Connecting to Telegram...")
    
    try:
        client = TelegramClient(StringSession(), api_id, api_hash)
        await client.connect()
        
        if await client.is_user_authorized():
            print("✅ Already authorized!")
        else:
            print(f"\n📲 Sending verification code to {phone}...")
            await client.send_code_request(phone)
            
            code = get_input("Enter the verification code you received")
            
            try:
                await client.sign_in(phone, code)
                print("✅ Successfully signed in!")
                
            except SessionPasswordNeededError:
                print("\n🔒 Your account has 2-Factor Authentication enabled.")
                password = get_input("Enter your 2FA password", password=True)
                
                try:
                    await client.sign_in(password=password)
                    print("✅ Successfully signed in with 2FA!")
                except Exception as e:
                    print(f"❌ 2FA sign-in failed: {e}")
                    return
                    
            except PhoneCodeInvalidError:
                print("❌ Invalid verification code!")
                return
            except Exception as e:
                print(f"❌ Sign-in failed: {e}")
                return
        
        # Generate and display session string
        session_string = StringSession.save(client.session)
        
        print("\n")
        print("╔══════════════════════════════════════════════════════════════╗")
        print("║           🎉 SESSION GENERATED SUCCESSFULLY! 🎉              ║")
        print("╚══════════════════════════════════════════════════════════════╝")
        print("\n")
        print("📋 Your Session String (copy everything between the lines):")
        print("─" * 70)
        print(session_string)
        print("─" * 70)
        print("\n")
        print("🔐 Next Steps:")
        print("─" * 70)
        print("1. Go to your GitHub repository")
        print("2. Navigate to: Settings → Secrets and variables → Actions")
        print("3. Add the following secrets:")
        print("")
        print("   TELEGRAM_API_ID          = " + str(api_id))
        print("   TELEGRAM_API_HASH        = " + api_hash)
        print("   TELEGRAM_SESSION_STRING  = [paste the session string above]")
        print("   TELEGRAM_TARGET_ENTITY   = me  (or @username, or chat_id)")
        print("─" * 70)
        print("\n✅ You're all set! Push to GitHub and the workflow will run.")
        
        await client.disconnect()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return


def main():
    try:
        asyncio.run(generate_session())
    except KeyboardInterrupt:
        print("\n\n👋 Setup cancelled by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    main()
