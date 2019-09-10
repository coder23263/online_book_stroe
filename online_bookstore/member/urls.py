from django.urls import path
from . import views


urlpatterns = [
    path('', views.member),
    path('shopping_cart/', views.shop_cart, name='shopping_cart'),
]