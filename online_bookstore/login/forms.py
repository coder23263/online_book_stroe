#encoding: utf-8
from django import forms
from django.core import validators
from django.db import connection

#获取sql_server的游标
cursor = connection.cursor()
class BaseForm(forms.Form):
    def get_errors(self):
        errors = self.errors.get_json_data()
        new_errors = {}
        for key, message_dicts in errors.items():
            messages = []
            for message_dict in message_dicts:
                message = message_dict['message']
                messages.append(message)
            new_errors[key] = messages
        return new_errors

class MyForm(BaseForm):#登录类
    account = forms.CharField(max_length=10)
    password = forms.CharField(max_length=20)


class RegisterForm(BaseForm):#注册类
    account = forms.CharField(max_length=10)
    name = forms.CharField(max_length=30)
    telephone = forms.CharField(validators=[validators.RegexValidator(r'1[345678]\d{9}')])
    email = forms.CharField(max_length=30)
    address = forms.CharField(max_length=50)
    pwd1 = forms.CharField(max_length=20)
    pwd2 = forms.CharField(max_length=20)

    #调用views.py中的is_valid()函数时自动调用clean_telephone（以clean开头，中间横线加上要验证的表单字段）
    def clean_account(self):#验证账户是否被注册过
        account = self.cleaned_data.get('account')#获取表单中的account
        cursor.execute("select * from MEMBER where mno={}".format(account))#获取db中的account
        try:
            db_account = cursor.fetchone()[0]
        except:
            db_account = ''
        if account == db_account.strip():
            raise forms.ValidationError(message='%s已经被注册！'%db_account)#在db中存在
        # 如果验证没有问题，一定要记得把telephone返回回去
        return account  #表单的account验证没有问题，返回

    def clean(self):#验证两次密码是否一致
        # 如果来到了clean方法，说明之前每一个字段都验证成功了
        cleaned_data = super().clean()
        pwd1 = cleaned_data.get('pwd1')
        pwd2 = cleaned_data.get('pwd2')
        if pwd1 != pwd2:
            raise forms.ValidationError(message='两次密码输入不一致！')
            print("密码不一致")
        return cleaned_data
