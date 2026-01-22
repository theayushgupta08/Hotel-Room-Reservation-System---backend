from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum


class RoomStatus(str, Enum):
    AVAILABLE = "available"
    BOOKED = "booked"


class Room(BaseModel):
    room_number: int
    floor: int
    position: int  # Position on floor (0-9 for floors 1-9, 0-6 for floor 10)
    status: RoomStatus
    guest_id: Optional[str] = None


class BookingRequest(BaseModel):
    num_rooms: int = Field(..., ge=1, le=5, description="Number of rooms to book (1-5)")
    guest_id: Optional[str] = None


class RoomPathInfo(BaseModel):
    room_number: int
    floor: int
    position: int
    steps: List[str]
    total_time: int  # in minutes


class BookingResponse(BaseModel):
    success: bool
    message: str
    booked_rooms: List[int]
    total_travel_time: Optional[int] = None  # in minutes
    room_paths: Optional[List[RoomPathInfo]] = None  # Path from reception to each room


class RoomStateResponse(BaseModel):
    rooms: Dict[int, Dict[str, Any]]
    total_rooms: int
    available_rooms: int
    booked_rooms: int


class RandomOccupancyRequest(BaseModel):
    occupancy_percentage: float = Field(..., ge=0, le=100, description="Percentage of rooms to occupy")


class MessageResponse(BaseModel):
    success: bool
    message: str
