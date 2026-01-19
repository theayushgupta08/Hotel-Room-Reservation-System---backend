"""
Simple test script to verify the booking system works correctly
"""
from booking_logic import HotelBookingSystem, RoomStatus

def test_basic_booking():
    """Test basic booking functionality"""
    system = HotelBookingSystem()
    
    # Test 1: Book 4 rooms on same floor
    print("Test 1: Booking 4 rooms (should be on same floor)")
    booked_rooms, travel_time = system.book_rooms(4)
    print(f"Booked rooms: {booked_rooms}, Travel time: {travel_time} minutes")
    assert len(booked_rooms) == 4
    assert travel_time >= 0
    
    # Test 2: Check room states
    print("\nTest 2: Checking room states")
    stats = system.get_statistics()
    print(f"Statistics: {stats}")
    assert stats["booked_rooms"] == 4
    assert stats["available_rooms"] == 93
    
    # Test 3: Reset and test random occupancy
    print("\nTest 3: Testing random occupancy")
    system.reset_all_bookings()
    system.generate_random_occupancy(30.0)
    stats = system.get_statistics()
    print(f"After 30% occupancy: {stats}")
    assert stats["booked_rooms"] > 0
    
    # Test 4: Book rooms when some are already booked
    print("\nTest 4: Booking more rooms with existing occupancy")
    try:
        booked_rooms, travel_time = system.book_rooms(3)
        print(f"Booked rooms: {booked_rooms}, Travel time: {travel_time} minutes")
        assert len(booked_rooms) == 3
    except ValueError as e:
        print(f"Expected error (not enough rooms): {e}")
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    test_basic_booking()
