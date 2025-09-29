"""Data models for the application"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class UserUpdate:
    """Data class for user update information"""
    user_id: str
    phone_number: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    last_synced: Optional[datetime] = None