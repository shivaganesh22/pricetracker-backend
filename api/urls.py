from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('s/',home),
    path('signup/',SignupView.as_view()),
    path('verifyemail/',VerificationView.as_view()),
    path('login/',LoginView.as_view()),
    path('logout/',SignOutView.as_view()),
    path('search/',SearchView.as_view()),
    path('product/',ProductView.as_view()),
    path('fcm/',FCMView.as_view()),
    path('alert/',AlertView.as_view()),
    path('alert/<int:id>/',AlertView.as_view()),
    path('forgotpassword/',ForgotView.as_view()),
    path('resetpassword/',ResetView.as_view()),
    path('contact/',ContactView.as_view()),
    path('send_fcm/',SendFCM.as_view()),


]
