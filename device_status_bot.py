import json
import os
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import pytz
from telegram import Bot
from telegram.constants import ParseMode
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DeviceStatusBot:
    def __init__(self, bot_token: str, chat_id: str, thread_id: int = None):
        """
        Initialize the Telegram bot for device status monitoring.
        
        Args:
            bot_token: Telegram bot token
            chat_id: Target chat ID (-1001324257791)
            thread_id: Topic/thread ID for groups with topics (28415)
        """
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id
        self.thread_id = thread_id
        self.device_states_dir = "device_states"
        self.message_id = None
        self.new_stock_requested = False  # Variable to track new stock requests
        
        # Timezone setup
        self.germany_tz = pytz.timezone('Europe/Berlin')
        self.istanbul_tz = pytz.timezone('Europe/Istanbul')
        
        # Detect RDP server
        self.rdp_server = self.detect_rdp_server()
    
    def detect_rdp_server(self) -> str:
        """Detect which RDP server we're running on by checking .env file."""
        try:
            table_id = os.getenv('AIRTABLE_TABLE_ID', '')
            
            if table_id == 'tblly72Bpidn8qE2v':
                return "🖥️ RDP #1"
            elif table_id == 'tbldc2IMldy0qig4X':
                return "🖥️ RDP #2"
            elif table_id == 'tblDymnELsmNKYz1g':
                return "🖥️ RDP #3"
            else:
                return "🖥️ Unknown Server"
        except Exception as e:
            logger.error(f"Error detecting RDP server: {e}")
            return "🖥️ Unknown Server"
    
    def load_device_data(self, device_number: int) -> Optional[Dict]:
        """Load device data from JSON file."""
        file_path = os.path.join(self.device_states_dir, f"DEVICE{device_number}.json")
        
        if not os.path.exists(file_path):
            logger.warning(f"Device file not found: {file_path}")
            return None
            
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return None
    
    def convert_timestamp(self, timestamp_str: str) -> str:
        """Convert timestamp from Germany to Istanbul timezone with custom format."""
        try:
            # Parse the timestamp (assuming it's in Germany timezone)
            dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            # If no timezone info, assume Germany timezone
            if dt.tzinfo is None:
                dt = self.germany_tz.localize(dt)
            
            # Convert to Istanbul timezone
            istanbul_dt = dt.astimezone(self.istanbul_tz)
            
            # Format as requested: 2025/8/2 12:43 PM
            formatted = istanbul_dt.strftime("%Y/%m/%d %I:%M %p")
            return formatted
            
        except Exception as e:
            logger.error(f"Error converting timestamp {timestamp_str}: {e}")
            return timestamp_str
    
    def calculate_progress(self, device_data: Dict) -> int:
        """Calculate farming progress percentage based on completed tasks."""
        completed_count = 0
        
        # Core story modes (4 fields) - 50%
        core_fields = ['EasyMode', 'HardMode', 'SideMode', 'SubStory']
        for field in core_fields:
            if device_data.get(field, 0) == 1:
                completed_count += 1
        
        if completed_count == 4:
            # Character slots (5 fields total) - 60%
            if device_data.get('Character_Slots_Purchased', 0) == 1:
                completed_count += 1
                
                # Exchange and giftbox (7 fields total) - 75%
                if (device_data.get('Exchange_Gold_Characters', 0) == 1 and 
                    device_data.get('Recive_GiftBox', 0) == 1):
                    completed_count += 2
                    
                    # Sorting and upgrade (11 fields total) - 90%
                    if (device_data.get('Sort_Characters_Lowest_Level', 0) == 1 and
                        device_data.get('Sort_Filter_Ascension', 0) == 1 and
                        device_data.get('Sort_Multi_Select_Garbage_First', 0) == 1 and
                        device_data.get('Upgrade_Characters_Level', 0) == 1):
                        completed_count += 4
        
        # Map completed count to percentage
        if completed_count >= 11:
            return 90
        elif completed_count >= 7:
            return 75
        elif completed_count >= 5:
            return 60
        elif completed_count >= 4:
            return 50
        else:
            return int((completed_count / 4) * 50)  # Proportional progress up to 50%
    
    def extract_device_info(self, device_data: Dict) -> Dict:
        """Extract only the required fields from device data."""
        if not device_data:
            return {}
            
        # Extract all status fields with their actual values
        status_fields = {
            "EasyMode": device_data.get("EasyMode", 0),
            "HardMode": device_data.get("HardMode", 0), 
            "SideMode": device_data.get("SideMode", 0),
            "SubStory": device_data.get("SubStory", 0),
            "Character_Slots_Purchased": device_data.get("Character_Slots_Purchased", 0),
            "Exchange_Gold_Characters": device_data.get("Exchange_Gold_Characters", 0),
            "Recive_GiftBox": device_data.get("Recive_GiftBox", 0),
            "Skip_Kon_Bonaza": device_data.get("Skip_Kon_Bonaza", 0),
            "Sort_Characters_Lowest_Level": device_data.get("Sort_Characters_Lowest_Level", 0),
            "Sort_Filter_Ascension": device_data.get("Sort_Filter_Ascension", 0),
            "Sort_Multi_Select_Garbage_First": device_data.get("Sort_Multi_Select_Garbage_First", 0)
        }
        
        # Extract additional info
        session_stats = device_data.get("SessionStats", {})
        last_task = session_stats.get("LastTaskExecuted", "N/A")
        last_updated = device_data.get("LastUpdated", "N/A")
        restarts_count = device_data.get("RestartingCount", 0)
        is_linked = device_data.get("isLinked", False)
        current_task_set = device_data.get("CurrentTaskSet", "")
        upgrade_characters_level = device_data.get("Upgrade_Characters_Level", 1)
        
        # Account info for linked accounts
        account_info = {
            "AccountID": device_data.get("AccountID", ""),
            "UserName": device_data.get("UserName", ""),
            "Email": device_data.get("Email", ""),
            "Password": device_data.get("Password", ""),
            "Orbs": device_data.get("Orbs", 0)
        }
        
        return {
            "status_fields": status_fields,
            "last_task": last_task,
            "last_updated": self.convert_timestamp(last_updated),
            "restarts_count": restarts_count,
            "is_linked": is_linked,
            "account_info": account_info,
            "current_task_set": current_task_set,
            "upgrade_characters_level": upgrade_characters_level
        }
    
    def get_device_status(self, device_data: Dict) -> str:
        """Determine device status for grouping."""
        if not device_data:
            return "No Data"
        
        # Check if synced to airtable (completed farming)
        if device_data.get("synced_to_airtable", False):
            return "Completed"
        
        # Check current task set for better status description
        current_task_set = device_data.get("CurrentTaskSet", "").lower()
        
        # Check story progression
        story_modes = ["EasyMode", "HardMode", "SideMode", "SubStory"]
        story_names = ["Easy Mode", "Hard Mode", "Side Mode", "Sub-Story"]
        
        for field, name in zip(story_modes, story_names):
            if device_data.get(field, 0) == 0:
                return f"Currently Completing {name} ~ Story"
        
        # Check other tasks
        if device_data.get("Character_Slots_Purchased", 0) == 0:
            return "Currently Completing Character Slots Purchase"
        
        if device_data.get("Exchange_Gold_Characters", 0) == 0:
            return "Currently Completing Gold Characters Exchange"
        
        if device_data.get("Recive_GiftBox", 0) == 0:
            return "Currently Completing Gift Box Reception"
        
        sort_fields = ["Sort_Characters_Lowest_Level", "Sort_Filter_Ascension", "Sort_Multi_Select_Garbage_First"]
        if any(device_data.get(field, 0) == 0 for field in sort_fields):
            return "Currently Completing Sorting Tasks"
        
        if device_data.get("Upgrade_Characters_Level", 0) == 0:
            return "Currently Completing Character Upgrades"
        
        return "Unknown Status"
    
    def create_full_message(self) -> str:
        """Create the complete message with grouped device information."""
        # Get current time
        now = datetime.now(self.istanbul_tz)
        current_time = now.strftime("%Y/%m/%d %I:%M %p")
        
        # Start message with server and time
        message = f"<b>{self.rdp_server}</b>\n"
        message += f"🕒 <b>{current_time}</b>\n\n"
        message += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # Group devices by status
        devices_by_status = defaultdict(list)
        completed_devices = []
        
        for device_num in range(1, 11):
            device_data = self.load_device_data(device_num)
            if not device_data:
                continue
            
            status = self.get_device_status(device_data)
            
            if status == "Completed":
                completed_devices.append((device_num, device_data))
            else:
                devices_by_status[status].append(device_num)
        
        # Show farming devices grouped by status
        if devices_by_status:
            for status, device_nums in sorted(devices_by_status.items()):
                count = len(device_nums)
                message += f"🟢 <b>x{count} DEVICE{'S' if count > 1 else ''}</b>\n"
                message += f"♻️ <i>{status}</i>\n\n"
        
        # Show completed devices individually
        if completed_devices:
            message += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            message += "✅ <b>COMPLETED FARMING</b>\n"
            message += "⏳ <i>Waiting For Others To Start New Stock</i>\n\n"
            
            for device_num, device_data in completed_devices:
                progress = self.calculate_progress(device_data)
                message += f"🖥️ <b>DEVICE {device_num}</b> • <b>{progress}% Complete</b>\n"
                message += f"🆔 <code>{device_data.get('AccountID', 'N/A')}</code>\n"
                message += f"👤 {device_data.get('UserName', 'N/A')}\n"
                message += f"💎 <b>{device_data.get('Orbs', 'N/A')}</b> Orbs\n\n"
        
        message += "━━━━━━━━━━━━━━━━━━━━━━\n"
        message += "🔄 <i>Updates every 5min</i>"
        
        return message
    
    def check_all_devices_linked(self) -> bool:
        """Check if all 10 devices have isLinked: true"""
        for device_num in range(1, 11):
            device_data = self.load_device_data(device_num)
            if not device_data or not device_data.get("isLinked", False):
                return False
        return True
    
    async def send_or_update_message(self):
        """Send a new message or update existing one with device status."""
        try:
            message_text = self.create_full_message()
            
            if self.message_id is None:
                # Send new message
                send_kwargs = {
                    "chat_id": self.chat_id,
                    "text": message_text,
                    "parse_mode": ParseMode.HTML
                }
                if self.thread_id:
                    send_kwargs["message_thread_id"] = self.thread_id
                    
                sent_message = await self.bot.send_message(**send_kwargs)
                self.message_id = sent_message.message_id
                logger.info(f"Sent new message with ID: {self.message_id} to thread: {self.thread_id}")
            else:
                # Update existing message
                edit_kwargs = {
                    "chat_id": self.chat_id,
                    "message_id": self.message_id,
                    "text": message_text,
                    "parse_mode": ParseMode.HTML
                }
                
                await self.bot.edit_message_text(**edit_kwargs)
                logger.info(f"Updated message ID: {self.message_id}")
                
        except Exception as e:
            error_message = str(e).lower()
            
            # Check if the error is because message was deleted or doesn't exist
            if any(phrase in error_message for phrase in [
                "message to edit not found", 
                "message can't be edited", 
                "bad request: message to edit not found",
                "message_id_invalid"
            ]):
                logger.warning(f"Original message not found, will send new message: {e}")
                self.message_id = None
                # Try to send a new message
                try:
                    await self.send_or_update_message()
                except Exception as retry_error:
                    logger.error(f"Failed to send new message after edit failed: {retry_error}")
            else:
                # For other errors, keep trying to update the same message
                logger.error(f"Error updating message (will retry with same message_id): {e}")
    
    async def start_monitoring(self):
        """Start the monitoring loop that updates every 5 minutes."""
        logger.info("Starting device status monitoring...")
        
        while True:
            try:
                await self.send_or_update_message()
                logger.info("Message updated successfully. Waiting 5 minutes...")
                await asyncio.sleep(300)  # 5 minutes = 300 seconds
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def handle_updates(self):
        """Handle incoming updates and commands."""
        offset = 0
        
        while True:
            try:
                # Get updates from Telegram
                updates = await self.bot.get_updates(offset=offset, timeout=10)
                
                for update in updates:
                    if update.message and update.message.text:
                        text = update.message.text.strip().lower()
                        chat_type = update.message.chat.type
                        username = update.message.from_user.username if update.message.from_user else "Unknown"
                        
                        # Handle /resend command - forces immediate update or new message  
                        if (text == "/resend" or 
                            text.startswith("/resend@") or 
                            "@bbs_farming_bot" in text.lower() and "/resend" in text):
                            
                            # Only reset message_id if explicitly requesting new message with /resend_new
                            if "new" in text:
                                self.message_id = None
                                logger.info(f"Forcing new message from {username} in {chat_type} chat")
                            
                            await self.send_or_update_message()
                            logger.info(f"Resent/updated status message from {username} in {chat_type} chat")
                        
                        # Handle /new_stock command - sets new stock requested flag only if all devices linked
                        elif (text == "/new_stock" or 
                              text.startswith("/new_stock@") or 
                              "@bbs_farming_bot" in text.lower() and "/new_stock" in text):
                            
                            if self.check_all_devices_linked():
                                self.new_stock_requested = True
                                
                                await self.bot.send_message(
                                    chat_id=update.message.chat_id,
                                    text="✅ New stock request received! Flag set for main project.",
                                    reply_to_message_id=update.message.message_id,
                                    **{"message_thread_id": self.thread_id} if self.thread_id else {}
                                )
                                logger.info(f"New stock requested from {username} in {chat_type} chat - Flag set to True")
                            else:
                                await self.bot.send_message(
                                    chat_id=update.message.chat_id,
                                    text="❌ Cannot request new stock - Not all devices are linked yet!",
                                    reply_to_message_id=update.message.message_id,
                                    **{"message_thread_id": self.thread_id} if self.thread_id else {}
                                )
                                logger.info(f"New stock request denied from {username} - Not all devices linked")
                    
                    offset = update.update_id + 1
                        
            except Exception as e:
                logger.error(f"Error handling updates: {e}")
                await asyncio.sleep(5)
    
    async def run_bot(self):
        """Run both status monitoring and command listening."""
        # Start both tasks concurrently
        await asyncio.gather(
            self.start_monitoring(),
            self.handle_updates()
        )

async def main():
    """Main function to run the bot."""
    # Configuration
    BOT_TOKEN = "8249078165:AAHcRuIdR4DGDUpMUJz7EEoC6GEt-CFMvB4"  # Your bot token
    
    # Updated to use group chat and specific topic/thread from the provided URL
    CHAT_ID = "-1001324257791"  # Group chat ID from https://t.me/c/1324257791/28415/43432
    THREAD_ID = 28415  # Topic/thread ID from the URL
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ Please set your BOT_TOKEN in the script!")
        print("You can get a bot token from @BotFather on Telegram")
        return
    
    # Create and start the bot with thread targeting
    bot = DeviceStatusBot(BOT_TOKEN, CHAT_ID, THREAD_ID)
    await bot.run_bot()

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())