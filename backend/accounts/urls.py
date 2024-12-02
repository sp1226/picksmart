# backend/accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view()),
    path('logout/', views.LogoutView.as_view()),
    path('signup/', views.SignupView.as_view()),
    path('check-login/', views.CheckLoginStatusView.as_view()),
    path('csrf/', views.GetCSRFToken.as_view()),
    path('profile/', views.UserProfileView.as_view()),
    path('analytics/', views.UserAnalyticsView.as_view()),
]