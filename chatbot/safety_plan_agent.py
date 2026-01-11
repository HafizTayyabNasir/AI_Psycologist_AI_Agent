# safety_plan_agent.py
# Safety Plan Agent - Generates personalized safety plans, handles escalation, and provides support

import os
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse
from .agent_utils import get_groq_client, detect_mental_health_concerns, detect_suicidal_keywords

# ===========================
# SAFETY PLAN AGENT CONFIGURATION
# ===========================

SAFETY_PLAN_AGENT_NAME = "Safety Plan Coordinator"

def generate_safety_plan_content(user_message, conversation_history, session_data):
    """
    Generate personalized safety plan content based on conversation
    
    Returns:
        dict: Safety plan content with sections
    """
    user_language = session_data.get("language") or "English"
    has_crisis = detect_suicidal_keywords(user_message) or detect_mental_health_concerns(user_message)
    
    # Extract key information from conversation
    plan_content = {
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "language": user_language,
        "risk_level": "CRISIS" if has_crisis else "HIGH",
        "sections": {
            "immediate_safety": [],
            "coping_strategies": [],
            "support_resources": [],
            "emergency_contacts": []
        }
    }
    
    # Generate personalized content based on conversation
    if user_language and ("urdu" in user_language.lower() or "hindi" in user_language.lower()):
        plan_content["sections"]["immediate_safety"] = [
            "Agar aap khud ko nuqsan pahunchane ki soch rahe hain, to pehle kisi se baat karein",
            "Kisi trusted person ke saath rehne ki koshish karein",
            "Emergency helpline par call karein (1166)",
            "Agar zarurat ho to nearest hospital jayen"
        ]
        plan_content["sections"]["coping_strategies"] = [
            "Gehri saans lein (deep breathing)",
            "Muslim prayer ya meditation karein",
            "Apni pasand ki music sunen",
            "Thoda walk karein ya exercise karein"
        ]
        plan_content["sections"]["support_resources"] = [
            "Mental Health Helpline: 1166",
            "Crisis Support: Aapki madad ke liye hamesha koi available hai",
            "Trusted friends ya family members se baat karein"
        ]
    else:
        plan_content["sections"]["immediate_safety"] = [
            "If you're thinking of harming yourself, reach out to someone first",
            "Stay with a trusted person if possible",
            "Call emergency helpline (1166 or local crisis line)",
            "Go to nearest hospital if needed"
        ]
        plan_content["sections"]["coping_strategies"] = [
            "Practice deep breathing exercises",
            "Use prayer or meditation",
            "Listen to calming music",
            "Take a walk or do light exercise"
        ]
        plan_content["sections"]["support_resources"] = [
            "Mental Health Helpline: 1166",
            "Crisis Support: Someone is always available to help",
            "Talk to trusted friends or family members"
        ]
    
    return plan_content

def trigger_human_escalation(user_message, session_data):
    """
    Trigger human escalation (doctor/moderator/helpline)
    
    Returns:
        dict: Escalation information
    """
    has_crisis = detect_suicidal_keywords(user_message) or detect_mental_health_concerns(user_message)
    
    escalation = {
        "triggered": has_crisis,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "priority": "URGENT" if has_crisis else "HIGH",
        "notified": True  # In real implementation, this would notify actual professionals
    }
    
    # In production, this would:
    # 1. Notify on-call doctor/psychiatrist
    # 2. Alert moderator/admin
    # 3. Trigger helpline callback
    # 4. Log to emergency response system
    
    return escalation

def get_support_message(user_language):
    """
    Get calm and respectful support message based on language
    """
    if user_language and ("urdu" in user_language.lower() or "hindi" in user_language.lower()):
        return "Main aapke saath hoon. Aapki safety hamari priority hai. Hum aapki madad kar rahe hain."
    else:
        return "I'm here with you. Your safety is our priority. We're working to support you."

def format_safety_plan_html(plan_content):
    """
    Format safety plan content as HTML with bold headings for chat display
    
    Returns:
        str: HTML formatted safety plan
    """
    user_language = plan_content.get("language") or "English"
    risk_level = plan_content.get("risk_level", "HIGH")
    created_at = plan_content.get("created_at", "N/A")
    sections = plan_content.get("sections", {})
    
    # Build HTML
    html_parts = []
    
    # Title
    if user_language and ("urdu" in user_language.lower() or "hindi" in user_language.lower()):
        title = "<h2 style='color: #4a9eff; margin-top: 20px; margin-bottom: 10px;'><strong>Personalized Safety Plan / شخصی حفاظتی منصوبہ</strong></h2>"
        section_titles = {
            "immediate_safety": "Immediate Safety Steps / فوری حفاظتی اقدامات",
            "coping_strategies": "Coping Strategies / نمٹنے کی حکمت عملی",
            "support_resources": "Support Resources / مدد کے وسائل",
            "emergency_contacts": "Emergency Contacts / ایمرجنسی رابطے"
        }
    else:
        title = "<h2 style='color: #4a9eff; margin-top: 20px; margin-bottom: 10px;'><strong>Personalized Safety Plan</strong></h2>"
        section_titles = {
            "immediate_safety": "Immediate Safety Steps",
            "coping_strategies": "Coping Strategies",
            "support_resources": "Support Resources",
            "emergency_contacts": "Emergency Contacts"
        }
    
    html_parts.append(title)
    html_parts.append(f"<p style='color: #ffffff; margin-bottom: 5px;'><strong>Generated:</strong> {created_at}</p>")
    html_parts.append(f"<p style='color: #ffffff; margin-bottom: 15px;'><strong>Risk Level:</strong> {risk_level}</p>")
    
    # Add sections
    for section_key, items in sections.items():
        if items:
            section_title = section_titles.get(section_key, section_key.replace("_", " ").title())
            html_parts.append(f"<h3 style='color: #66bb6a; margin-top: 15px; margin-bottom: 8px;'><strong>{section_title}</strong></h3>")
            html_parts.append("<ul style='color: #ffffff; margin-left: 20px; margin-bottom: 10px;'>")
            for item in items:
                html_parts.append(f"<li style='color: #ffffff; margin-bottom: 5px;'>{item}</li>")
            html_parts.append("</ul>")
    
    return "<div style='background-color: #1a1a1a; padding: 15px; border-radius: 8px; border-left: 4px solid #4a9eff; color: #ffffff;'>" + "".join(html_parts) + "</div>"

def generate_pdf(plan_content, user_id=None):
    """
    Generate PDF from safety plan content
    
    Returns:
        bytes: PDF file content
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for PDF elements
    story = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        alignment=1,  # Center alignment
        textColor=(0.2, 0.3, 0.6)
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        spaceAfter=12,
        spaceBefore=12,
        textColor=(0.3, 0.5, 0.8)
    )
    
    # Title
    user_language = plan_content.get("language") or "English"
    if user_language and ("urdu" in user_language.lower() or "hindi" in user_language.lower()):
        title_text = "Personalized Safety Plan<br/>شخصی حفاظتی منصوبہ"
    else:
        title_text = "Personalized Safety Plan"
    
    story.append(Paragraph(title_text, title_style))
    story.append(Spacer(1, 0.2*inch))
    
    # Date
    date_text = f"Generated: {plan_content.get('created_at', 'N/A')}"
    story.append(Paragraph(date_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Risk Level
    risk_level = plan_content.get("risk_level", "HIGH")
    risk_text = f"<b>Risk Level: {risk_level}</b>"
    story.append(Paragraph(risk_text, styles['Normal']))
    story.append(Spacer(1, 0.3*inch))
    
    # Sections
    sections = plan_content.get("sections", {})
    
    if user_language and ("urdu" in user_language.lower() or "hindi" in user_language.lower()):
        section_titles = {
            "immediate_safety": "Immediate Safety Steps<br/>فوری حفاظتی اقدامات",
            "coping_strategies": "Coping Strategies<br/>نمٹنے کی حکمت عملی",
            "support_resources": "Support Resources<br/>مدد کے وسائل",
            "emergency_contacts": "Emergency Contacts<br/>ایمرجنسی رابطے"
        }
    else:
        section_titles = {
            "immediate_safety": "Immediate Safety Steps",
            "coping_strategies": "Coping Strategies",
            "support_resources": "Support Resources",
            "emergency_contacts": "Emergency Contacts"
        }
    
    for section_key, items in sections.items():
        if items:
            story.append(Paragraph(section_titles.get(section_key, section_key.title()), heading_style))
            for item in items:
                story.append(Paragraph(f"• {item}", styles['Normal']))
                story.append(Spacer(1, 0.1*inch))
            story.append(Spacer(1, 0.2*inch))
    
    # Build PDF
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

def process_safety_plan(user_message, conversation_history, session_data, user_id=None):
    """
    Process safety plan generation and escalation
    
    Returns:
        dict: Safety plan data, escalation info, support message, and HTML formatted plan
    """
    # Generate safety plan content
    plan_content = generate_safety_plan_content(user_message, conversation_history, session_data)
    
    # Trigger human escalation
    escalation = trigger_human_escalation(user_message, session_data)
    
    # Get support message
    user_language = session_data.get("language") or "English"
    support_message = get_support_message(user_language)
    
    # Format safety plan as HTML for chat display
    safety_plan_html = format_safety_plan_html(plan_content)
    
    return {
        "plan_content": plan_content,
        "escalation": escalation,
        "support_message": support_message,
        "safety_plan_html": safety_plan_html
    }

