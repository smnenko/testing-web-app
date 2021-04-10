from django.urls import path
from .views import authorize, register, index, login_out

urlpatterns = [
    path('', index),
    path('login', authorize),
    path('register', register),
    path('logout', login_out)
]
