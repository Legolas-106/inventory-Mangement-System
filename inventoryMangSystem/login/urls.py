from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),  # User registration endpoint
    path('login', views.login, name='login'),  # Login endpoint
    path('token', views.token_retrieve, name='token_retrieve'),  # Token retrieval endpoint
]
