from django.urls import path
from . import views

urlpatterns = [
    path('score/', views.predict_risk, name='predict_risk'),
]
