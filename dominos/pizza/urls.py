from django.urls import path
from . import views


app_name = 'pizza'
urlpatterns = [
    
    path('',views.home, name='home'),
    path('payment/',views.payment, name='payment'),
]
    
    
