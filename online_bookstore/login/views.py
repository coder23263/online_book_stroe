from django.shortcuts import render
from django.views.generic import View
from .forms import MyForm, RegisterForm
from django.http import HttpResponse
from django.db import connection
from django.shortcuts import reverse, redirect
from shopping.views import shopping_cart

cursor = connection.cursor()
class IndexView(View):
    def get(self,request):
        return render(request,'login.html')

    def verify_ID(self, account, password):  # 验证身份函数,传入前端得到的账号密码(str类型)，传出TURE or FALSE
        cursor.execute("select * from MEMBER where mno={}".format(account))  # 调用游标指针的execute方法执行sql语句
        db_password = cursor.fetchone()[1]
        if password == db_password.strip():
            return True

    def post(self,request):
        form = MyForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data.get('account')
            password = form.cleaned_data.get('password')
            is_success_or_fail = self.verify_ID(account, password)
            if is_success_or_fail:
                #print("登录成功")
                #登录成功之后设置cookies
                response = redirect(reverse('shopping'))#得到response对象，预备设置cookies值
                response.set_cookie('account', account)#为response对象设置cookies值
                return response#若登录成功，页面重定向到购物页面
            else:
                print("登录失败  %s"%password)
                return HttpResponse('请输入正确的密码')
        else:
            print(form.errors.get_json_data())
            return redirect(reverse('signin'))


class RegisterView(View):
    def get(self,request):
        return render(request,'register.html')

    def post(self,request):
        form = RegisterForm(request.POST)
        if form.is_valid():#如果注册信息验证成功，插入sql_server
            account = form.cleaned_data.get('account')
            password = form.cleaned_data.get('pwd1')
            name = form.cleaned_data.get('name')
            telephone = form.cleaned_data.get('telephone')
            email = form.cleaned_data.get('email')
            address = form.cleaned_data.get('address')
            #插入数据
            cursor.execute("INSERT INTO MEMBER(mno, mpassword, mname, mphone, mpost, madress) VALUES ('{}','{}','{}','{}','{}','{}')".format(account, password, name, telephone, email, address))
            return HttpResponse('注册成功！')
        else:
            print(form.get_errors())
            return HttpResponse('注册失败！')

def logout(request):#删除cookies并反转到shopping页面
    global shopping_cart
    response = redirect(reverse('shopping'))
    response.delete_cookie('account')
    shopping_cart = dict()
    return response
