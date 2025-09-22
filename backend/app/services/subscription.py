from datetime import datetime, timedelta
from typing import Dict, List
from app.models.schemas import SubscriptionTier

class SubscriptionService:
    """Service to handle subscription-based feature access"""
    
    # Subscription tier limits
    TIER_LIMITS = {
        SubscriptionTier.BASIC: {
            "case_study_weekly_limit": 5,
            "expert_advice_weekly_limit": 0,
            "chat_advice_limit": None,  # Unlimited
            "features": ["chat_advice", "case_study_limited"]
        },
        SubscriptionTier.STANDARD: {
            "case_study_weekly_limit": None,  # Unlimited
            "expert_advice_weekly_limit": 0,
            "chat_advice_limit": None,  # Unlimited
            "features": ["chat_advice", "case_study_unlimited"]
        },
        SubscriptionTier.PREMIUM: {
            "case_study_weekly_limit": None,  # Unlimited
            "expert_advice_weekly_limit": 3,
            "chat_advice_limit": None,  # Unlimited
            "features": ["chat_advice", "case_study_unlimited", "expert_advice_limited"]
        },
        SubscriptionTier.PLATINUM: {
            "case_study_weekly_limit": None,  # Unlimited
            "expert_advice_weekly_limit": None,  # Unlimited
            "chat_advice_limit": None,  # Unlimited
            "features": ["chat_advice", "case_study_unlimited", "expert_advice_unlimited"]
        }
    }
    
    def __init__(self, db):
        self.db = db
    
    def check_feature_access(self, user_id: str, feature: str) -> bool:
        """Check if user has access to a specific feature"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return False
        
        tier = SubscriptionTier(user.get("subscription_tier", "Basic"))
        tier_features = self.TIER_LIMITS[tier]["features"]
        
        return feature in tier_features
    
    def check_case_study_limit(self, user_id: str) -> Dict[str, any]:
        """Check case study usage limits for user"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {"allowed": False, "reason": "User not found"}
        
        tier = SubscriptionTier(user.get("subscription_tier", "Basic"))
        weekly_limit = self.TIER_LIMITS[tier]["case_study_weekly_limit"]
        
        # If unlimited access
        if weekly_limit is None:
            return {"allowed": True, "remaining": "unlimited"}
        
        # Count case studies in the last 7 days
        case_studies = self.db.get_user_case_studies(user_id)
        week_ago = datetime.now() - timedelta(days=7)
        
        recent_studies = [
            study for study in case_studies 
            if datetime.fromisoformat(study["created_at"]) > week_ago
        ]
        
        used_count = len(recent_studies)
        remaining = max(0, weekly_limit - used_count)
        
        return {
            "allowed": remaining > 0,
            "remaining": remaining,
            "used": used_count,
            "limit": weekly_limit,
            "resets_at": (datetime.now() + timedelta(days=7)).isoformat()
        }
    
    def check_expert_advice_limit(self, user_id: str) -> Dict[str, any]:
        """Check expert advice usage limits for user"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {"allowed": False, "reason": "User not found"}
        
        tier = SubscriptionTier(user.get("subscription_tier", "Basic"))
        weekly_limit = self.TIER_LIMITS[tier]["expert_advice_weekly_limit"]
        
        # If no access
        if weekly_limit == 0:
            return {"allowed": False, "reason": f"{tier.value} tier doesn't include expert advice"}
        
        # If unlimited access
        if weekly_limit is None:
            return {"allowed": True, "remaining": "unlimited"}
        
        # Count bookings in the last 7 days
        bookings = self.db.get_user_bookings(user_id)
        week_ago = datetime.now() - timedelta(days=7)
        
        recent_bookings = [
            booking for booking in bookings 
            if datetime.fromisoformat(booking["created_at"]) > week_ago
        ]
        
        used_count = len(recent_bookings)
        remaining = max(0, weekly_limit - used_count)
        
        return {
            "allowed": remaining > 0,
            "remaining": remaining,
            "used": used_count,
            "limit": weekly_limit,
            "resets_at": (datetime.now() + timedelta(days=7)).isoformat()
        }
    
    def get_subscription_info(self, user_id: str) -> Dict[str, any]:
        """Get comprehensive subscription information for user"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {"error": "User not found"}
        
        tier = SubscriptionTier(user.get("subscription_tier", "Basic"))
        tier_info = self.TIER_LIMITS[tier]
        
        # Get usage information
        case_study_info = self.check_case_study_limit(user_id)
        expert_advice_info = self.check_expert_advice_limit(user_id)
        
        return {
            "current_tier": tier.value,
            "features": tier_info["features"],
            "limits": {
                "case_study": {
                    "weekly_limit": tier_info["case_study_weekly_limit"],
                    "usage": case_study_info
                },
                "expert_advice": {
                    "weekly_limit": tier_info["expert_advice_weekly_limit"],
                    "usage": expert_advice_info
                },
                "chat_advice": {
                    "limit": tier_info["chat_advice_limit"]  # Always unlimited
                }
            },
            "subscription_expiry": user.get("subscription_expiry")
        }
    
    def upgrade_subscription(self, user_id: str, new_tier: SubscriptionTier, duration_months: int = 1) -> bool:
        """Upgrade user subscription"""
        if new_tier == SubscriptionTier.BASIC:
            # Basic is free, no expiry
            expiry = None
        else:
            # Paid tiers have expiry dates
            expiry = (datetime.now() + timedelta(days=30 * duration_months)).isoformat()
        
        update_data = {
            "subscription_tier": new_tier.value,
            "subscription_expiry": expiry
        }
        
        return self.db.update_user(user_id, update_data)
    
    def check_subscription_expiry(self, user_id: str) -> Dict[str, any]:
        """Check if subscription has expired and downgrade if necessary"""
        user = self.db.get_user_by_id(user_id)
        if not user:
            return {"error": "User not found"}
        
        expiry_date = user.get("subscription_expiry")
        if not expiry_date:
            return {"expired": False, "message": "No expiry date set"}
        
        expiry = datetime.fromisoformat(expiry_date)
        if datetime.now() > expiry:
            # Downgrade to Basic
            self.db.update_user(user_id, {
                "subscription_tier": SubscriptionTier.BASIC.value,
                "subscription_expiry": None
            })
            return {"expired": True, "downgraded_to": SubscriptionTier.BASIC.value}
        
        return {"expired": False, "expires_at": expiry_date}