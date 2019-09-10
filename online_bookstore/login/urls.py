from django.urls import path
from . import views


urlpatterns = [
    path('', views.IndexView.as_view(), name='signin'),
    path('register/', views.RegisterView.as_view(), name='signup'),
    path('logout/', views.logout, name='logout'),
]
