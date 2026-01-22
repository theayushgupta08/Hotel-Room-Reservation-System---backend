from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from models import (
    BookingRequest, 
    BookingResponse,
    RoomPathInfo,
    RoomStateResponse,
    RandomOccupancyRequest,
    MessageResponse
)
from booking_logic import HotelBookingSystem
import uvicorn

app = FastAPI(
    title="Hotel Room Reservation System",
    description="Backend API for hotel room booking with optimal room assignment",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://hotel-room-reservation-system-backe-iota.vercel.app", "http://localhost:5173"],  # Allow all origins
    allow_credentials=False,  # Must be False when using wildcard origins
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
)

# Initialize the booking system
booking_system = HotelBookingSystem()


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Hotel Room Reservation System API",
        "version": "1.0.0",
        "endpoints": {
            "GET /rooms": "Get all room states",
            "POST /book": "Book rooms",
            "POST /random-occupancy": "Generate random occupancy",
            "POST /reset": "Reset all bookings",
            "GET /statistics": "Get booking statistics"
        }
    }


@app.get("/rooms", response_model=RoomStateResponse)
async def get_rooms():
    """Get current state of all rooms"""
    states = booking_system.get_room_states()
    stats = booking_system.get_statistics()
    
    return RoomStateResponse(
        rooms=states,
        total_rooms=stats["total_rooms"],
        available_rooms=stats["available_rooms"],
        booked_rooms=stats["booked_rooms"]
    )


@app.post("/book", response_model=BookingResponse)
async def book_rooms(request: BookingRequest):
    """Book rooms based on optimal assignment rules"""
    try:
        booked_rooms, travel_time, room_paths = booking_system.book_rooms(
            num_rooms=request.num_rooms,
            guest_id=request.guest_id
        )
        
        # Convert room paths to RoomPathInfo models
        path_info_list = [
            RoomPathInfo(
                room_number=path["room_number"],
                floor=path["floor"],
                position=path["position"],
                steps=path["steps"],
                total_time=path["total_time"]
            )
            for path in room_paths
        ]
        
        return BookingResponse(
            success=True,
            message=f"Successfully booked {len(booked_rooms)} room(s)",
            booked_rooms=booked_rooms,
            total_travel_time=travel_time,
            room_paths=path_info_list
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/random-occupancy", response_model=MessageResponse)
async def generate_random_occupancy(request: RandomOccupancyRequest):
    """Generate random occupancy for rooms"""
    try:
        booking_system.generate_random_occupancy(request.occupancy_percentage)
        stats = booking_system.get_statistics()
        
        return MessageResponse(
            success=True,
            message=f"Generated random occupancy: {stats['booked_rooms']} rooms booked ({request.occupancy_percentage}% of total)"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.post("/reset", response_model=MessageResponse)
async def reset_bookings():
    """Reset all room bookings"""
    try:
        booking_system.reset_all_bookings()
        return MessageResponse(
            success=True,
            message="All bookings have been reset"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@app.get("/statistics")
async def get_statistics():
    """Get booking statistics"""
    return booking_system.get_statistics()

# Export app for Vercel (ASGI support)
# Vercel will automatically detect and use the 'app' variable
if __name__ == "__main__":
    uvicorn.run(app, port=8000)
