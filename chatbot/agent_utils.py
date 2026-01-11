# agent_utils.py
# Shared utilities for both agents

import os
from dotenv import load_dotenv
from groq import Groq

# ===========================
# LOAD ENV + GROQ INIT
# ===========================

load_dotenv()
client = None
try:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("🔴 FATAL ERROR: GROQ_API_KEY not found in .env file.")
    else:
        client = Groq(api_key=api_key)
        print(f"✅ Groq client initialized successfully.")
except Exception as e:
    print(f"🔴 FATAL ERROR during Groq initialization: {e}")

def get_groq_client():
    """Get the initialized Groq client"""
    return client

# ===========================
# SESSION MANAGEMENT
# ===========================

def get_user_session(request):
    """Get or create user session data using Django sessions"""
    # Initialize session if not exists
    if not request.session.session_key:
        request.session.create()
    
    # Get session data from Django session
    session_data = request.session.get('chatbot_data')
    if session_data is None:
        session_data = {
            "current_agent": "orchestrator",  # 'orchestrator' or 'interview'
            "language": None,
            "conversation_history": [],
            "referred_to_interview": False
        }
        request.session['chatbot_data'] = session_data
    
    return session_data

def save_user_session(request, session_data):
    """Save user session data to Django session"""
    request.session['chatbot_data'] = session_data
    request.session.modified = True

# ===========================
# DETECTION FUNCTIONS
# ===========================

def detect_suicidal_keywords(text):
    """Detect suicidal keywords and phrases in multiple languages - CRITICAL for immediate referral"""
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Suicidal ideation indicators (English)
    suicidal_keywords_english = [
        'suicide', 'kill myself', 'end my life', 'want to die', 'better off dead',
        'not worth living', 'suicidal', 'self-harm', 'hurt myself', 'end it all',
        'taking my life', 'ending it', 'wish i was dead'
    ]
    
    # Suicidal ideation indicators (Urdu/Hindi - transliterated and common phrases)
    suicidal_keywords_urdu = [
        'khud kushi', 'khudkushi', 'apne aap ko mar', 'mar jana', 'jan dena',
        'zindagi khatam', 'khatam karna', 'khatam kar dena', 'marna chahta',
        'marna chahunga', 'marne ki soch', 'suicide'
    ]
    
    suicidal_keywords = suicidal_keywords_english + suicidal_keywords_urdu
    
    for keyword in suicidal_keywords:
        if keyword in text_lower:
            return True
    
    return False

def detect_mental_health_concerns(text):
    """Detect keywords and phrases indicating mental health concerns in multiple languages"""
    if not text:
        return False
    
    text_lower = text.lower()
    
    # Suicidal ideation indicators (English)
    suicidal_keywords_english = [
        'suicide', 'kill myself', 'end my life', 'want to die', 'better off dead',
        'not worth living', 'suicidal', 'self-harm', 'hurt myself', 'end it all',
        'kill myself', 'taking my life', 'ending it', 'want to die', 'wish i was dead'
    ]
    
    # Suicidal ideation indicators (Urdu/Hindi - transliterated and common phrases)
    suicidal_keywords_urdu = [
        'khud kushi', 'khudkushi', 'apne aap ko mar', 'mar jana', 'jan dena',
        'zindagi khatam', 'khatam karna', 'khatam kar dena', 'marna chahta',
        'marna chahunga', 'marne ki soch', 'suicide', 'kisi'
    ]
    
    # Severe depression/hopelessness indicators
    hopelessness_keywords = [
        'hopeless', 'no point', 'no future', 'nothing matters', 'can\'t go on',
        'give up', 'despair', 'helpless', 'worthless', 'deep depression',
        'severe depression', 'major depression', 'umsaid', 'be umeed', 'nirash'
    ]
    
    # Crisis indicators
    crisis_keywords = [
        'emergency', 'crisis', 'urgent help', 'immediate danger', 'can\'t cope',
        'overwhelmed', 'breakdown', 'panic attack', 'severe anxiety'
    ]
    
    all_keywords = suicidal_keywords_english + suicidal_keywords_urdu + hopelessness_keywords + crisis_keywords
    
    for keyword in all_keywords:
        if keyword in text_lower:
            return True
    
    return False

def detect_referral_request(text):
    """Detect if user wants to be referred to interview agent"""
    if not text:
        return False
    
    text_lower = text.lower()
    referral_indicators = [
        'yes', 'sure', 'okay', 'ok', 'yes please', 'connect me', 'speak with specialist',
        'talk to psychiatrist', 'interview', 'assessment', 'help me', 'need help'
    ]
    
    for indicator in referral_indicators:
        if indicator in text_lower:
            return True
    
    return False

def detect_language_preference(message):
    """Detect language preference from user message"""
    if not message:
        return None
    
    message_lower = message.lower()
    
    # Check for explicit language mentions
    if any(word in message_lower for word in ['urdu', 'اردو', 'hindi', 'हिंदी', 'i speak urdu', 'i speak hindi']):
        return "Urdu/Hindi"
    elif any(word in message_lower for word in ['spanish', 'español', 'i speak spanish']):
        return "Spanish"
    elif any(word in message_lower for word in ['french', 'français', 'i speak french']):
        return "French"
    elif any(word in message_lower for word in ['arabic', 'عربي', 'i speak arabic']):
        return "Arabic"
    elif any(word in message_lower for word in ['english', 'i speak english']):
        return "English"
    
    # Auto-detect from actual text content (Urdu/Hindi)
    urdu_hindi_indicators = [
        'میں', 'آپ', 'ہے', 'ہیں', 'کر', 'کے', 'کی', 'سے', 'کو', 'پر', 'اور', 'لیکن', 'تھا', 'تھی',
        'mein', 'aap', 'hai', 'hain', 'kar', 'ke', 'ki', 'se', 'ko', 'par', 'aur', 'lekin', 'tha', 'thi',
        'mujhe', 'tum', 'tu', 'main', 'tumhara', 'tumhari', 'tumhare', 'apna', 'apne', 'apni',
        'मैं', 'आप', 'है', 'हैं', 'कर', 'के', 'की', 'से', 'को', 'पर', 'और', 'लेकिन', 'था', 'थी',
        'मुझे', 'तुम', 'तू', 'मैन', 'तुम्हारा', 'तुम्हारी', 'तुम्हारे', 'अपना', 'अपने', 'अपनी'
    ]
    
    if any(indicator in message for indicator in urdu_hindi_indicators):
        return "Urdu/Hindi"
    
    return None
