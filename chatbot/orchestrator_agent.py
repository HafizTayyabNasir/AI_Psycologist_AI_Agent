# orchestrator_agent.py
# Orchestrator Agent (Main Controller) - Handles general conversations and routing

from .agent_utils import get_groq_client, detect_mental_health_concerns, detect_referral_request, detect_language_preference, detect_suicidal_keywords

# ===========================
# ORCHESTRATOR AGENT CONFIGURATION
# ===========================

ORCHESTRATOR_AGENT_NAME = "Mental Health Support Orchestrator"
ORCHESTRATOR_WELCOME_MESSAGE = """Hello! I'm here to support you. I'm a mental health support assistant who can help you with general conversations and connect you with specialized psychiatric support when needed.

Before we begin, in which language would you prefer to communicate? (You can respond in English, Urdu, Spanish, or any language you're comfortable with.)

I'm here to listen and help. Feel free to share what's on your mind."""

ORCHESTRATOR_SYSTEM_INSTRUCTIONS = f"""
You are {ORCHESTRATOR_AGENT_NAME}, a compassionate and empathetic mental health support assistant.

Your primary responsibilities:
1. **Language Preference**: If the user hasn't specified a language yet, ask them which language they prefer for communication (English, Urdu, Spanish, French, Arabic, or any other language).

2. **General Conversation**: 
   - Engage in warm, supportive, and empathetic general conversations. Be a good listener and provide emotional support.
   - **CRITICAL**: If a user indicates they are fine ("theek hoon", "I'm okay", "theek taak", etc.), RESPECT their response. Do NOT keep asking probing questions or repeat yourself.
   - Allow natural conversation flow. Only ask follow-up questions if the user genuinely seems to want to talk or if there are actual warning signs.
   - DO NOT over-interrogate users who are having casual conversations. Match the user's energy level and engagement.
   - If user is clearly fine and just chatting casually, respond naturally without forcing mental health topics.

3. **Mental Health Risk Assessment** (CRITICAL - Execute on EVERY message):
   For EVERY single user message, you MUST:
   
   a) **Language-Aware Analysis**: Thoroughly analyze each message in the language the user is communicating in:
      - If user writes in English → analyze in English
      - If user writes in Urdu script (اردو) → analyze in Urdu
      - If user writes in Roman Urdu (transliterated Urdu/Hindi using English letters) → analyze in Roman Urdu
      - Apply the same language awareness to other languages (Spanish, Arabic, French, etc.)
   
   b) **Risk Level Classification**: Assess and categorize the risk level for each message in the user's language:
      - **LOW**: General conversation, minimal distress, normal emotional expression
      - **MODERATE**: Some emotional distress, mild concerns, but manageable
      - **HIGH**: Significant mental health concerns, severe distress, clear warning signs
      - **CRISIS**: Suicidal ideation, immediate danger, severe mental health crisis, or ANY uncertainty
   
   c) **CRISIS Detection Indicators** (adapt based on user's language):
      - English: "suicide", "kill myself", "end my life", "want to die", "hopeless", "no point"
      - Urdu/Roman Urdu: "khud kushi", "khudkushi", "mar jana", "jan dena", "khatam karna", "be umeed", "nirash"
      - Spanish: "suicidio", "matarme", "sin esperanza", "sin futuro"
      - And equivalent phrases in other languages based on context
      - Also watch for: severe hopelessness, despair, severe depression, anxiety/panic, immediate danger to self or others
   
   d) **CRITICAL SAFETY RULE - "When in Doubt, Treat as CRISIS"**:
      If there is ANY uncertainty, ambiguity, or slight doubt about the risk level → ALWAYS classify as **CRISIS**.
      It is better to err on the side of caution. Patient safety is paramount.
   
   e) **MANDATORY: Include Risk Assessment in Response**:
      At the END of EVERY response, you MUST include the risk assessment in this format:
      "\n\n(LANGUAGE-AWARE RISK ASSESSMENT: [RISK_LEVEL])\nRisk Level: [RISK_LEVEL]\nNext Step: [Brief description of next action based on risk level]"
      Where [RISK_LEVEL] is one of: LOW, MODERATE, HIGH, or CRISIS
      Examples:
      - For LOW: "Next Step: Continue natural conversation, monitor for escalation"
      - For MODERATE: "Next Step: Continue supportive conversation, show empathy, monitor for escalation"
      - For HIGH: "Next Step: Immediately refer to interview agent for detailed assessment"
      - For CRISIS: "Next Step: IMMEDIATE referral to interview agent - CRISIS situation detected"

4. **Agent Routing Based on Risk Assessment**:
   - **For LOW risk**: Engage in natural, casual conversation. Do NOT probe unnecessarily. If user is fine and chatting, respond naturally without forcing mental health discussions.
   - **For MODERATE risk**: Continue supportive conversation, show empathy, but don't over-interrogate. Monitor for escalation while maintaining natural flow.
   - **For HIGH/CRISIS risk**: 
     * Respond immediately with empathy and understanding
     * Inform the user: "I think it would be helpful for you to speak with our psychiatric interview specialist. They can conduct a more detailed assessment to better understand your situation. Would you like me to connect you with them?"
     * ALWAYS respond with: "[REFER_TO_INTERVIEW_AGENT]" when risk is HIGH or CRISIS
     * For CRISIS level: Do not wait for user confirmation - immediately respond with "[REFER_TO_INTERVIEW_AGENT]" after your empathetic response

5. **Communication Style**:
   - Be warm, empathetic, non-judgmental, and supportive
   - **CRITICAL LANGUAGE MATCHING**: You MUST respond in the EXACT same language and format the user is using:
     * If user writes in English → respond in English
     * If user writes in Roman Urdu (Urdu in English letters like "mein", "aap", "kaise", "hai") → respond in Roman Urdu
     * If user writes in Urdu script (اردو) → respond in Urdu script
     * If user writes in Hindi script (हिंदी) → respond in Hindi script
     * If user writes in Spanish → respond in Spanish
     * Match the user's language format EXACTLY - do NOT switch languages mid-conversation
   - Never dismiss or minimize their feelings
   - Maintain professional boundaries while being caring
   - Always prioritize user safety and wellbeing
   - **DO NOT be repetitive**: Avoid asking the same question multiple times or repeating yourself
   - **DO NOT be intrusive**: If user says they're fine, accept it and engage in normal conversation
   - **Match user's tone**: If user is casual and fine, be casual. If user is distressed, be more supportive
   - Keep responses concise and natural - don't over-explain or be unnecessarily verbose

6. **Important**: 
   - Do NOT mention AI, language models, or technical details
   - Focus on being present, listening, and providing emotional support
   - When mental health concerns are detected, always offer the interview agent referral

Remember: Your role is to be a first point of contact and to identify when specialized psychiatric support is needed.

**CRITICAL REMINDER**: On EVERY message, you MUST perform the language-aware risk assessment (LOW/MODERATE/HIGH/CRISIS) in the user's communication language. When in doubt, always classify as CRISIS and immediately refer to the interview agent. Safety first. However, for LOW risk users who are fine, engage naturally without being intrusive or repetitive.
"""

def get_welcome_message():
    """Get the orchestrator welcome message"""
    return ORCHESTRATOR_WELCOME_MESSAGE

def process_message(user_message, user_content, conversation_history, session_data):
    """
    Process a message with the orchestrator agent
    
    Returns:
        tuple: (bot_response, should_switch_to_interview, updated_session_data)
    """
    client = get_groq_client()
    if not client:
        return "The AI model is not configured. Please check server logs.", False, session_data
    
    # Add language detection from user message if not set (needed for immediate referral message)
    user_language = session_data.get("language")
    if not user_language:
        detected_language = detect_language_preference(user_message)
        if detected_language:
            user_language = detected_language
            session_data["language"] = user_language
    
    # CRITICAL: Check for suicidal keywords FIRST - immediate referral required
    has_suicidal_keywords = detect_suicidal_keywords(user_message)
    if has_suicidal_keywords:
        # IMMEDIATE REFERRAL - Do not proceed with orchestrator, switch immediately
        session_data["referred_to_interview"] = True
        # Generate language-appropriate referral message
        if user_language and ("urdu" in user_language.lower() or "hindi" in user_language.lower()):
            referral_message = "Main aapko psychiatric interview specialist se connect kar raha hoon. Woh aapki safety ka assessment karenge. Please stay with me."
        else:
            referral_message = "I'm connecting you with our psychiatric interview specialist now. They can conduct a safety assessment to better understand your situation. Please stay with me."
        return referral_message, True, session_data
    
    # Check if we should switch to interview agent
    has_mental_health_concern = detect_mental_health_concerns(user_message)
    referred_to_interview = session_data.get("referred_to_interview", False)
    should_switch = False
    
    # Language detection already done above - continue if still not detected
    if not user_language:
        # If not detected from current message, check conversation history
        for hist_msg in reversed(conversation_history[-3:]):  # Check last 3 messages
            if hist_msg.get("role") == "user":
                detected_language = detect_language_preference(hist_msg.get("content", ""))
                if detected_language:
                    user_language = detected_language
                    session_data["language"] = user_language
                    break
    
    # Prepare system instructions with language requirement
    system_instructions = ORCHESTRATOR_SYSTEM_INSTRUCTIONS
    
    # Add STRONG language preference to system instructions if set
    if user_language:
        if "urdu" in user_language.lower() or "hindi" in user_language.lower() or "اردو" in user_language or "हिंदी" in user_language:
            system_instructions += f"\n\n🚨 CRITICAL LANGUAGE REQUIREMENT 🚨\n\nThe user has been communicating in Urdu/Hindi (including Roman Urdu - Urdu written in English letters). You MUST respond in the SAME language format the user is using:\n- If user writes in Roman Urdu (English letters like 'mein', 'aap', 'kaise', 'hai') → You MUST respond in Roman Urdu\n- If user writes in Urdu script (اردو) → You MUST respond in Urdu script\n- If user writes in Hindi script (हिंदी) → You MUST respond in Hindi script\nDO NOT switch to English. Match the user's language format exactly. Use phrases like 'Main aap ke saath hoon', 'Aap kaise hain?', 'Kya aapko koi pareshan hai?', 'Bataiye kya ho raha hai?' Continue the conversation in the SAME language and format the user is using to maintain connection and trust."
        elif "spanish" in user_language.lower():
            system_instructions += f"\n\n🚨 CRITICAL LANGUAGE REQUIREMENT 🚨\n\nThe user has been communicating in Spanish. You MUST respond in Spanish. DO NOT switch to English. Continue the conversation in Spanish to maintain connection and trust."
        elif "french" in user_language.lower():
            system_instructions += f"\n\n🚨 CRITICAL LANGUAGE REQUIREMENT 🚨\n\nThe user has been communicating in French. You MUST respond in French. DO NOT switch to English. Continue the conversation in French to maintain connection and trust."
        elif "arabic" in user_language.lower():
            system_instructions += f"\n\n🚨 CRITICAL LANGUAGE REQUIREMENT 🚨\n\nThe user has been communicating in Arabic. You MUST respond in Arabic. DO NOT switch to English. Continue the conversation in Arabic to maintain connection and trust."
    
    # Build messages for orchestrator
    messages = [{"role": "system", "content": system_instructions}]
    
    # Add conversation history (last 10 messages for context)
    for hist_msg in conversation_history[-10:]:
        messages.append(hist_msg)
    
    # Add current user message
    messages.append({"role": "user", "content": user_content})
    
    # Call Groq API (Orchestrator Agent)
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
            stream=True,
        )
    except Exception as model_error:
        # Fallback to alternative model if primary fails
        print(f"⚠️ Primary model failed, trying alternative: {model_error}")
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True,
            )
        except Exception as fallback_error:
            # Final fallback
            print(f"⚠️ Fallback model failed, trying fallback: {fallback_error}")
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=0.7,
                max_tokens=2048,
                stream=True,
            )
    
    # Collect streamed response
    bot_response = ""
    try:
        for chunk in completion:
            if chunk.choices and len(chunk.choices) > 0:
                if chunk.choices[0].delta and chunk.choices[0].delta.content:
                    bot_response += chunk.choices[0].delta.content
    except Exception as stream_error:
        print(f"⚠️ Error during streaming: {stream_error}")
    
    if not bot_response:
        bot_response = "I'm here to listen. Could you tell me more about what you're experiencing?"
    
    # Check if orchestrator response contains referral marker (AI decided to refer)
    if "[REFER_TO_INTERVIEW_AGENT]" in bot_response:
        bot_response = bot_response.replace("[REFER_TO_INTERVIEW_AGENT]", "").strip()
        should_switch = True
    # If orchestrator previously suggested interview and user agrees, switch now
    elif referred_to_interview and detect_referral_request(user_message):
        should_switch = True
        bot_response += "\n\nI'm connecting you with our psychiatric interview specialist now. They can conduct a more detailed assessment to better understand your situation."
    # If severe mental health concern detected, mark for referral (orchestrator will offer next)
    elif has_mental_health_concern:
        session_data["referred_to_interview"] = True
    
    return bot_response, should_switch, session_data
