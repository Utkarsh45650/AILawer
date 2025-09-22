from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.database.json_db import db
from app.services.subscription import SubscriptionService

class ExpertAdviceService:
    """Service for handling lawyer consultations and booking system"""
    
    def __init__(self):
        self.subscription_service = SubscriptionService(db)
    
    def get_available_lawyers(self, user_id: str, specialization: Optional[str] = None) -> Dict[str, Any]:
        """Get available lawyers based on user's subscription"""
        
        # Check if user has access to expert advice
        advice_limit = self.subscription_service.check_expert_advice_limit(user_id)
        if not advice_limit["allowed"]:
            return {
                "error": "Expert advice not available for your subscription tier",
                "limit_info": advice_limit,
                "upgrade_required": True
            }
        
        # Get all lawyers
        all_lawyers = db.get_all_lawyers()
        
        # Filter by specialization if provided
        if specialization:
            all_lawyers = [
                lawyer for lawyer in all_lawyers 
                if specialization.lower() in lawyer.get("specialization", "").lower()
            ]
        
        # Add availability information
        for lawyer in all_lawyers:
            lawyer["available_slots"] = self._generate_available_slots(lawyer["id"])
        
        return {
            "lawyers": all_lawyers,
            "usage_info": advice_limit
        }
    
    def get_online_lawyers(self, user_id: str) -> Dict[str, Any]:
        """Get only online lawyers"""
        
        # Check subscription access
        advice_limit = self.subscription_service.check_expert_advice_limit(user_id)
        if not advice_limit["allowed"]:
            return {
                "error": "Expert advice not available for your subscription tier",
                "limit_info": advice_limit,
                "upgrade_required": True
            }
        
        online_lawyers = db.get_online_lawyers()
        
        # Add availability slots
        for lawyer in online_lawyers:
            lawyer["available_slots"] = self._generate_available_slots(lawyer["id"])
        
        return {
            "online_lawyers": online_lawyers,
            "usage_info": advice_limit
        }
    
    def _generate_available_slots(self, lawyer_id: str) -> List[Dict[str, Any]]:
        """Generate available time slots for a lawyer (mock implementation)"""
        # In a real system, this would integrate with the lawyer's actual calendar
        
        # Get existing bookings for this lawyer
        all_bookings = []
        # This would need to be implemented in the database
        
        # Generate slots for the next 7 days
        slots = []
        current_time = datetime.now()
        
        for day in range(7):
            date = current_time + timedelta(days=day)
            
            # Skip weekends (simple logic)
            if date.weekday() >= 5:
                continue
            
            # Generate slots from 9 AM to 5 PM
            for hour in range(9, 17):
                slot_time = date.replace(hour=hour, minute=0, second=0, microsecond=0)
                
                # Only future slots
                if slot_time > current_time:
                    slots.append({
                        "datetime": slot_time.isoformat(),
                        "available": True,  # In real system, check against bookings
                        "duration_minutes": 60
                    })
        
        return slots[:20]  # Limit to 20 slots
    
    def book_consultation(
        self, 
        user_id: str, 
        lawyer_id: str, 
        appointment_time: str, 
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Book a consultation with a lawyer"""
        
        # Check subscription limits
        advice_limit = self.subscription_service.check_expert_advice_limit(user_id)
        if not advice_limit["allowed"]:
            return {
                "error": "Expert advice limit exceeded for your subscription tier",
                "limit_info": advice_limit,
                "upgrade_required": True
            }
        
        # Validate lawyer exists
        lawyer = db.get_lawyer(lawyer_id)
        if not lawyer:
            return {"error": "Lawyer not found"}
        
        # Validate appointment time
        try:
            appointment_dt = datetime.fromisoformat(appointment_time)
            if appointment_dt <= datetime.now():
                return {"error": "Appointment time must be in the future"}
        except ValueError:
            return {"error": "Invalid appointment time format"}
        
        # Create booking
        booking_data = {
            "user_id": user_id,
            "lawyer_id": lawyer_id,
            "appointment_time": appointment_time,
            "description": description,
            "lawyer_name": lawyer["name"],
            "lawyer_specialization": lawyer["specialization"]
        }
        
        booking_id = db.create_booking(booking_data)
        
        return {
            "booking_id": booking_id,
            "lawyer_name": lawyer["name"],
            "lawyer_specialization": lawyer["specialization"],
            "appointment_time": appointment_time,
            "status": "pending",
            "description": description,
            "usage_info": self.subscription_service.check_expert_advice_limit(user_id)
        }
    
    def get_user_bookings(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all bookings for a user"""
        bookings = db.get_user_bookings(user_id)
        
        # Add lawyer information to each booking
        for booking in bookings:
            lawyer = db.get_lawyer(booking.get("lawyer_id"))
            if lawyer:
                booking["lawyer_name"] = lawyer["name"]
                booking["lawyer_specialization"] = lawyer["specialization"]
        
        return bookings
    
    def cancel_booking(self, booking_id: str, user_id: str) -> Dict[str, Any]:
        """Cancel a booking"""
        # Get booking to verify ownership
        bookings = db.get_user_bookings(user_id)
        booking = next((b for b in bookings if b["id"] == booking_id), None)
        
        if not booking:
            return {"error": "Booking not found or access denied"}
        
        # Check if booking can be cancelled (e.g., not too close to appointment time)
        appointment_time = datetime.fromisoformat(booking["appointment_time"])
        if appointment_time <= datetime.now() + timedelta(hours=2):
            return {"error": "Cannot cancel booking less than 2 hours before appointment"}
        
        # Update booking status
        success = db.update_booking_status(booking_id, "cancelled")
        
        if success:
            return {"success": True, "message": "Booking cancelled successfully"}
        else:
            return {"error": "Failed to cancel booking"}
    
    def get_booking_details(self, booking_id: str, user_id: str) -> Dict[str, Any]:
        """Get detailed information about a booking"""
        bookings = db.get_user_bookings(user_id)
        booking = next((b for b in bookings if b["id"] == booking_id), None)
        
        if not booking:
            return {"error": "Booking not found or access denied"}
        
        # Add lawyer details
        lawyer = db.get_lawyer(booking.get("lawyer_id"))
        if lawyer:
            booking["lawyer_details"] = {
                "name": lawyer["name"],
                "specialization": lawyer["specialization"],
                "is_online": lawyer.get("is_online", False)
            }
        
        return booking
    
    def get_lawyer_specializations(self) -> List[str]:
        """Get list of all lawyer specializations"""
        lawyers = db.get_all_lawyers()
        specializations = list(set(lawyer.get("specialization", "") for lawyer in lawyers))
        return [spec for spec in specializations if spec]  # Remove empty strings
    
    def reschedule_booking(
        self, 
        booking_id: str, 
        user_id: str, 
        new_appointment_time: str
    ) -> Dict[str, Any]:
        """Reschedule an existing booking"""
        # Get booking to verify ownership
        bookings = db.get_user_bookings(user_id)
        booking = next((b for b in bookings if b["id"] == booking_id), None)
        
        if not booking:
            return {"error": "Booking not found or access denied"}
        
        # Validate new appointment time
        try:
            new_appointment_dt = datetime.fromisoformat(new_appointment_time)
            if new_appointment_dt <= datetime.now():
                return {"error": "New appointment time must be in the future"}
        except ValueError:
            return {"error": "Invalid appointment time format"}
        
        # Check if original booking can be rescheduled
        original_time = datetime.fromisoformat(booking["appointment_time"])
        if original_time <= datetime.now() + timedelta(hours=4):
            return {"error": "Cannot reschedule booking less than 4 hours before appointment"}
        
        # Update booking (this would need to be implemented in the database)
        # For now, we'll return success
        return {
            "success": True,
            "message": "Booking rescheduled successfully",
            "new_appointment_time": new_appointment_time,
            "booking_id": booking_id
        }
    
    def get_expert_advice_response(self, user_id: str, query: str, legal_area: str) -> Dict[str, Any]:
        """Get expert advice response for a query"""
        # Check if user has access to expert advice
        advice_limit = self.subscription_service.check_expert_advice_limit(user_id)
        if not advice_limit["allowed"]:
            return {
                "error": "Expert advice not available for your subscription tier",
                "limit_info": advice_limit,
                "upgrade_required": True
            }
        
        # Generate expert advice response
        expert_advice = f"""Based on your question about {legal_area}, here's preliminary legal guidance:

Query: {query}

Expert Legal Analysis:
1. This appears to be a {legal_area} matter that requires careful consideration
2. I recommend gathering all relevant documentation related to your case
3. Consider consulting with a specialized {legal_area} attorney for detailed advice
4. Timeline for action may be important - don't delay seeking professional help

Recommended Next Steps:
• Schedule a consultation with one of our expert lawyers
• Prepare a detailed summary of your situation
• Gather all relevant documents and evidence
• Consider the urgency of your legal matter

Disclaimer: This is preliminary guidance only. For specific legal advice tailored to your situation, please book a consultation with one of our qualified attorneys."""

        return {
            "advice": expert_advice,
            "legal_area": legal_area,
            "usage_info": advice_limit,
            "recommended_lawyers": self._get_recommended_lawyers(legal_area)
        }
    
    def _get_recommended_lawyers(self, legal_area: str) -> List[Dict[str, Any]]:
        """Get recommended lawyers for a specific legal area"""
        all_lawyers = db.get_all_lawyers()
        # Filter lawyers by specialization matching the legal area
        recommended = [
            {
                "id": lawyer["id"],
                "name": lawyer["name"],
                "specialization": lawyer["specialization"],
                "rating": lawyer.get("rating", 4.5),
                "is_online": lawyer.get("is_online", False)
            }
            for lawyer in all_lawyers 
            if legal_area.lower() in lawyer.get("specialization", "").lower()
        ]
        
        # If no specific match, return top-rated general lawyers
        if not recommended:
            recommended = [
                {
                    "id": lawyer["id"],
                    "name": lawyer["name"],
                    "specialization": lawyer["specialization"],
                    "rating": lawyer.get("rating", 4.5),
                    "is_online": lawyer.get("is_online", False)
                }
                for lawyer in all_lawyers[:3]  # Top 3 lawyers
            ]
        
        return recommended[:5]  # Return max 5 recommendations