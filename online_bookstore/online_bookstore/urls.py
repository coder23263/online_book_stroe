from django.urls import path, include
from . import views



urlpatterns = [
    path('', views.home, name='home'),
    path('shopping/', include('shopping.urls')),
    path('member/', include('member.urls')),
    path('login/', include('login.urls')),
    path('manager/', include('manager.urls')),
]
