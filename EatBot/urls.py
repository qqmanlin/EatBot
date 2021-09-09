from django.urls import path
from EatBot import views

urlpatterns = [
    path('callback', views.callback)
]
