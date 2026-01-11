from django.urls import path
from . import views

urlpatterns = [
    path('', views.chatbot_view, name='chatbot'),
    path('ask/', views.ask_gemini_view, name='ask_gemini'),
    path('download-safety-plan/', views.download_safety_plan, name='download_safety_plan'),
]