"""
Database module for storing bot data
"""
import json
import os
from typing import Dict, List

DB_FILE = "bot_data.json"

def load_data() -> Dict:
    """Load data from database"""
    if not os.path.exists(DB_FILE):
        return {
            "groups": {},
            "channels": {},
            "stats": {
                "reactions_added": 0,
                "messages_processed": 0
            }
        }
    
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except:
        return {
            "groups": {},
            "channels": {},
            "stats": {
                "reactions_added": 0,
                "messages_processed": 0
            }
        }

def save_data(data: Dict):
    """Save data to database"""
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def add_group(group_id: int, group_name: str) -> bool:
    """Add group to monitor"""
    data = load_data()
    if group_id not in data["groups"]:
        data["groups"][str(group_id)] = {
            "name": group_name,
            "enabled": True
        }
        save_data(data)
        return True
    return False

def remove_group(group_id: int) -> bool:
    """Remove group from monitoring"""
    data = load_data()
    if str(group_id) in data["groups"]:
        del data["groups"][str(group_id)]
        save_data(data)
        return True
    return False

def add_channel(channel_id: int, channel_name: str) -> bool:
    """Add channel to monitor"""
    data = load_data()
    if channel_id not in data["channels"]:
        data["channels"][str(channel_id)] = {
            "name": channel_name,
            "enabled": True
        }
        save_data(data)
        return True
    return False

def remove_channel(channel_id: int) -> bool:
    """Remove channel from monitoring"""
    data = load_data()
    if str(channel_id) in data["channels"]:
        del data["channels"][str(channel_id)]
        save_data(data)
        return True
    return False

def get_groups() -> Dict:
    """Get all monitored groups"""
    data = load_data()
    return data["groups"]

def get_channels() -> Dict:
    """Get all monitored channels"""
    data = load_data()
    return data["channels"]

def increment_reactions():
    """Increment reaction counter"""
    data = load_data()
    data["stats"]["reactions_added"] += 1
    save_data(data)

def increment_messages():
    """Increment message counter"""
    data = load_data()
    data["stats"]["messages_processed"] += 1
    save_data(data)

def get_stats() -> Dict:
    """Get bot statistics"""
    data = load_data()
    return {
        "reactions_added": data["stats"]["reactions_added"],
        "messages_processed": data["stats"]["messages_processed"],
        "groups_count": len(data["groups"]),
        "channels_count": len(data["channels"])
    }
