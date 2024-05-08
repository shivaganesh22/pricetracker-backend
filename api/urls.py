from django.contrib import admin
from django.urls import path
from .views import *
urlpatterns = [
    path('s/',home),
    path('signup/',SignupView.as_view()),
    path('login/',LoginView.as_view()),
    path('logout/',SignOutView.as_view()),
    path('search/',SearchView.as_view()),
    path('product/',ProductView.as_view()),

]
