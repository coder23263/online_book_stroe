from django.urls import path, include
from . import views


urlpatterns = [
    path('', views.ManageView.as_view(), name='manager_login'),
    path('root_admin/<deal>/', views.root_admin, name='manage'),

]