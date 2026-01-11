import json
import base64
import traceback
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from PIL import Image
import io

from .agent_utils import get_groq_client, get_user_session, save_user_session
from .orchestrator_agent import get_welcome_message as get_orchestrator_welcome, process_message as process_orchestrator_message
from .interview_agent import get_welcome_message as get_interview_welcome

@login_required
def chatbot_view(request):
    session_data = get_user_session(request)
    session_data["current_agent"] = "orchestrator"
    session_data["language"] = None
    session_data["conversation_history"] = []
    session_data["referred_to_interview"] = False
    save_user_session(request, session_data)
    
    return render(
        request,
        "chatbot/chatbot.html",
        {"initial_bot_message": get_orchestrator_welcome()}
    )

@csrf_exempt
def ask_gemini_view(request):
    client = get_groq_client()
    if not client:
        return JsonResponse(
            {"error": "The AI model is not configured. Please check server logs."},
            status=500,
        )

    if request.method != "POST":
        return JsonResponse({"error": "Invalid request method"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))
        user_message = data.get("message", "").strip()
        base64_image = data.get("image")

        if not user_message and not base64_image:
            return JsonResponse(
                {"error": "Please provide a message."}, status=400
            )

        session_data = get_user_session(request)
        current_agent = session_data.get("current_agent", "orchestrator")
        conversation_history = session_data.get("conversation_history", [])
        user_language = session_data.get("language")

        user_content = user_message if user_message else "Hello"
        if base64_image:
            try:
                header, encoded = base64_image.split(";base64,")
                image_bytes = base64.b64decode(encoded)
                image = Image.open(io.BytesIO(image_bytes))
                image_format = image.format or 'image'
                user_content = f"{user_message}\n\n[Note: An image ({image_format}) was attached, but image analysis may be limited in this context.]"
            except Exception as img_exc:
                print("⚠️ Image decoding error:", img_exc)

        if current_agent == "orchestrator":
            bot_response, should_switch, session_data = process_orchestrator_message(
                user_message, user_content, conversation_history, session_data
            )
            
            if should_switch:
                current_agent = "interview"
                session_data["current_agent"] = "interview"
                session_data["referred_to_interview"] = True
                interview_welcome = get_interview_welcome(
                    language=session_data.get("language"),
                    conversation_history=conversation_history
                )
                if "I'm a psychiatric interview specialist" not in bot_response:
                    bot_response += "\n\n" + interview_welcome
        else:
            from .interview_agent import process_message as process_interview_message
            bot_response = process_interview_message(
                user_message, user_content, conversation_history, session_data
            )
            
            from .safety_plan_agent import process_safety_plan
            safety_plan_data = process_safety_plan(
                user_message, conversation_history, session_data, user_id=request.user.id
            )
            
            bot_response += "<br/><br/>" + safety_plan_data["safety_plan_html"]
        
        conversation_history.append({"role": "user", "content": user_content})
        conversation_history.append({"role": "assistant", "content": bot_response})
        session_data["conversation_history"] = conversation_history
        session_data["language"] = session_data.get("language")
        save_user_session(request, session_data)
        
        return JsonResponse({
            "response": bot_response,
            "current_agent": current_agent,
            "language": session_data.get("language"),
            "safety_plan_available": current_agent == "interview"
        })

    except Exception as e:
        print("\n🔴 EXCEPTION IN ask_gemini_view 🔴")
        traceback.print_exc()
        return JsonResponse(
            {"error": f"An unexpected server error occurred: {str(e)}"},
            status=500,
        )

@login_required
def download_safety_plan(request):
    session_data = get_user_session(request)
    pdf_base64 = session_data.get("safety_plan_pdf")
    
    if not pdf_base64:
        return JsonResponse({"error": "Safety plan not available"}, status=404)
    
    import base64
    pdf_bytes = base64.b64decode(pdf_base64)
    
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="safety_plan.pdf"'
    return response
