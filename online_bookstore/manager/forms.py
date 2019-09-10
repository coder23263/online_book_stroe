#encoding: utf-8
from django import forms
from django.core import validators
from django.db import connection

#获取sql_server的游标
cursor = connection.cursor()

class managerForm(forms.Form):#登录类
    account = forms.CharField(max_length=10)
    password = forms.CharField(max_length=20)