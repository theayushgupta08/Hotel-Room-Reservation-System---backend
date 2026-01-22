from typing import List, Dict, Tuple, Optional
from models import Room, RoomStatus
import random
from itertools import combinations


class HotelBookingSystem:
    def __init__(self):
        self.rooms: Dict[int, Room] = {}
        self._initialize_rooms()
    
    def _initialize_rooms(self):
        """Initialize all 97 rooms in the hotel"""
        # Floors 1-9: 10 rooms each
        for floor in range(1, 10):
            for pos in range(10):
                room_number = floor * 100 + (pos + 1)
                self.rooms[room_number] = Room(
                    room_number=room_number,
                    floor=floor,
                    position=pos,
                    status=RoomStatus.AVAILABLE
                )
        
        # Floor 10: 7 rooms (1001-1007)
        for pos in range(7):
            room_number = 1000 + (pos + 1)
            self.rooms[room_number] = Room(
                room_number=room_number,
                floor=10,
                position=pos,
                status=RoomStatus.AVAILABLE
            )
    
    def get_room(self, room_number: int) -> Optional[Room]:
        """Get room by room number"""
        return self.rooms.get(room_number)
    
    def get_available_rooms(self) -> List[Room]:
        """Get all available rooms"""
        return [room for room in self.rooms.values() if room.status == RoomStatus.AVAILABLE]
    
    def calculate_travel_time(self, room1: Room, room2: Room) -> int:
        """
        Calculate travel time between two rooms
        - Horizontal: 1 minute per room
        - Vertical: 2 minutes per floor
        """
        if room1.floor == room2.floor:
            # Same floor: only horizontal travel
            return abs(room1.position - room2.position)
        else:
            # Different floors: vertical + horizontal
            vertical_time = abs(room1.floor - room2.floor) * 2
            horizontal_time = room1.position + room2.position  # Travel to stairs + from stairs
            return vertical_time + horizontal_time
    
    def calculate_travel_time_from_reception(self, room: Room) -> int:
        """
        Calculate travel time from ground floor reception (floor 0, position 0) to a room
        - Vertical: 2 minutes per floor (from floor 0 to room floor)
        - Horizontal: 1 minute per room position (from stairs to room)
        """
        vertical_time = room.floor * 2  # From floor 0 to room floor
        horizontal_time = room.position  # From stairs (position 0) to room position
        return vertical_time + horizontal_time
    
    def get_path_from_reception(self, room: Room) -> Dict[str, Any]:
        """
        Get the path description from reception to a room
        Returns a dictionary with path steps and total time
        Reception is at floor 0, position 0 (stairs location)
        """
        steps = []
        total_time = 0
        
        # Step 1: Go up floors (from floor 0 to room floor)
        if room.floor > 0:
            steps.append(f"Take stairs/lift up {room.floor} floor(s) ({room.floor * 2} minutes)")
            total_time += room.floor * 2
        
        # Step 2: Walk to room from stairs (if not at position 0)
        if room.position > 0:
            steps.append(f"Walk {room.position} room(s) from stairs to Room {room.room_number} ({room.position} minutes)")
            total_time += room.position
        elif room.floor > 0:
            steps.append(f"Room {room.room_number} is located at the stairs on Floor {room.floor}")
        
        # If room is on floor 0 (ground floor)
        if room.floor == 0:
            if room.position > 0:
                steps.append(f"Walk {room.position} room(s) from reception to Room {room.room_number} ({room.position} minutes)")
                total_time += room.position
            else:
                steps.append("Room is at the reception area")
        
        return {
            "steps": steps,
            "total_time": total_time,
            "room_number": room.room_number,
            "floor": room.floor,
            "position": room.position
        }
    
    def calculate_total_travel_time(self, rooms: List[Room]) -> int:
        """
        Calculate total travel time for a list of rooms
        (time from first to last room)
        """
        if len(rooms) <= 1:
            return 0
        
        # Sort rooms by floor and position
        sorted_rooms = sorted(rooms, key=lambda r: (r.floor, r.position))
        first_room = sorted_rooms[0]
        last_room = sorted_rooms[-1]
        
        return self.calculate_travel_time(first_room, last_room)
    
    def find_rooms_on_same_floor(self, num_rooms: int) -> Optional[List[Room]]:
        """Find available rooms on the same floor, prioritizing consecutive rooms"""
        available_by_floor: Dict[int, List[Room]] = {}
        
        for room in self.get_available_rooms():
            if room.floor not in available_by_floor:
                available_by_floor[room.floor] = []
            available_by_floor[room.floor].append(room)
        
        # Check each floor for enough rooms
        for floor in sorted(available_by_floor.keys()):
            floor_rooms = sorted(available_by_floor[floor], key=lambda r: r.position)
            if len(floor_rooms) >= num_rooms:
                # Try to find consecutive rooms first
                best_consecutive = self._find_consecutive_rooms(floor_rooms, num_rooms)
                if best_consecutive:
                    return best_consecutive
                # If no consecutive rooms, return first N rooms
                return floor_rooms[:num_rooms]
        
        return None
    
    def _find_consecutive_rooms(self, sorted_rooms: List[Room], num_rooms: int) -> Optional[List[Room]]:
        """Find consecutive rooms from a sorted list"""
        if len(sorted_rooms) < num_rooms:
            return None
        
        # Try to find consecutive rooms
        for i in range(len(sorted_rooms) - num_rooms + 1):
            consecutive = sorted_rooms[i:i + num_rooms]
            positions = [r.position for r in consecutive]
            # Check if positions are consecutive
            if all(positions[j] == positions[0] + j for j in range(len(positions))):
                return consecutive
        
        return None
    
    def find_optimal_rooms(self, num_rooms: int) -> List[Room]:
        """
        Find optimal rooms based on booking rules:
        1. Same floor first (preferably consecutive)
        2. Minimize total travel time across floors
        """
        # Rule 1: Try to find rooms on the same floor
        same_floor_rooms = self.find_rooms_on_same_floor(num_rooms)
        if same_floor_rooms:
            return same_floor_rooms
        
        # Rule 2: If not available on same floor, minimize travel time
        available_rooms = self.get_available_rooms()
        
        if len(available_rooms) < num_rooms:
            return []  # Not enough rooms available
        
        # Optimize: Try to minimize combinations by grouping by floor first
        # Then try combinations of floors, prioritizing adjacent floors
        best_rooms = self._find_optimal_cross_floor_rooms(available_rooms, num_rooms)
        
        return best_rooms if best_rooms else []
    
    def _find_optimal_cross_floor_rooms(self, available_rooms: List[Room], num_rooms: int) -> List[Room]:
        """Find optimal rooms across multiple floors"""
        # Group by floor
        rooms_by_floor: Dict[int, List[Room]] = {}
        for room in available_rooms:
            if room.floor not in rooms_by_floor:
                rooms_by_floor[room.floor] = []
            rooms_by_floor[room.floor].append(room)
        
        # Sort rooms on each floor by position
        for floor in rooms_by_floor:
            rooms_by_floor[floor].sort(key=lambda r: r.position)
        
        # Try all combinations (with max 5 rooms, this is manageable)
        best_rooms = None
        min_travel_time = float('inf')
        
        for combo in combinations(available_rooms, num_rooms):
            travel_time = self.calculate_total_travel_time(list(combo))
            if travel_time < min_travel_time:
                min_travel_time = travel_time
                best_rooms = list(combo)
        
        return best_rooms
    
    def book_rooms(self, num_rooms: int, guest_id: Optional[str] = None) -> Tuple[List[int], int, List[Dict[str, Any]]]:
        """
        Book rooms and return list of booked room numbers, total travel time, and individual room paths
        """
        if num_rooms < 1 or num_rooms > 5:
            raise ValueError("Number of rooms must be between 1 and 5")
        
        optimal_rooms = self.find_optimal_rooms(num_rooms)
        
        if len(optimal_rooms) < num_rooms:
            raise ValueError(f"Not enough rooms available. Requested: {num_rooms}, Available: {len(self.get_available_rooms())}")
        
        # Book the rooms
        booked_room_numbers = []
        room_paths = []
        for room in optimal_rooms:
            room.status = RoomStatus.BOOKED
            room.guest_id = guest_id
            booked_room_numbers.append(room.room_number)
            # Get path from reception for each room
            path_info = self.get_path_from_reception(room)
            room_paths.append(path_info)
        
        # Calculate total travel time
        total_travel_time = self.calculate_total_travel_time(optimal_rooms)
        
        return booked_room_numbers, total_travel_time, room_paths
    
    def reset_all_bookings(self):
        """Reset all room bookings"""
        for room in self.rooms.values():
            room.status = RoomStatus.AVAILABLE
            room.guest_id = None
    
    def generate_random_occupancy(self, occupancy_percentage: float):
        """Generate random occupancy for rooms"""
        self.reset_all_bookings()
        
        total_rooms = len(self.rooms)
        num_to_book = int(total_rooms * occupancy_percentage / 100)
        
        available_room_numbers = list(self.rooms.keys())
        random.shuffle(available_room_numbers)
        
        for i in range(min(num_to_book, len(available_room_numbers))):
            room = self.rooms[available_room_numbers[i]]
            room.status = RoomStatus.BOOKED
            room.guest_id = f"guest_{random.randint(1000, 9999)}"
    
    def get_room_states(self) -> Dict[int, Dict[str, any]]:
        """Get current state of all rooms"""
        states = {}
        for room_number, room in self.rooms.items():
            states[room_number] = {
                "room_number": room.room_number,
                "floor": room.floor,
                "position": room.position,
                "status": room.status.value,
                "guest_id": room.guest_id
            }
        return states
    
    def get_statistics(self) -> Dict[str, int]:
        """Get booking statistics"""
        total = len(self.rooms)
        booked = sum(1 for room in self.rooms.values() if room.status == RoomStatus.BOOKED)
        available = total - booked
        
        return {
            "total_rooms": total,
            "booked_rooms": booked,
            "available_rooms": available
        }
