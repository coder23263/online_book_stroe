from django.shortcuts import render
from django.views.generic import View
from .forms import managerForm
from django.http import HttpResponse
from django.db import connection
from django.shortcuts import reverse, redirect
from datetime import datetime
import pandas as pd
cursor = connection.cursor()

class ManageView(View):
    def get(self, request):
        return render(request, 'login_for_manager.html')

    def verify_ID(self, account, password):  # 验证身份账号密码(str类型)，传出TURE or FALSE,默认管理员账户为 root，密码为23263
        if account == 'root' and password == '23263':
            return True
        else:
            return False

    def post(self,request):
        form = managerForm(request.POST)
        if form.is_valid():
            account = form.cleaned_data.get('account')
            password = form.cleaned_data.get('password')
            is_success_or_fail = self.verify_ID(account, password)
            if is_success_or_fail:
                #登录成功之后设置cookies
                response = redirect(reverse('manage', kwargs={"deal": 'index'}))#得到response对象，预备设置cookies值
                response.set_cookie('manager_account', 'ROOT_ROOT')#为response对象设置cookies值为root  , path='/manager/root_admin/'
                return response#若登录成功，页面重定向到购物页面
            else:
                return HttpResponse('请输入正确的账号密码')
        else:
            print(form.errors.get_json_data())
            return redirect(reverse('manager_login'))


def root_admin(request, deal):
    cookies = request.COOKIES
    if cookies.get('manager_account') == 'ROOT_ROOT':
        context = dict()#创建一个空字典来储存传递到html页面的内容

        if request.method == 'GET':#get方法不同参数渲染不同的页面
            if deal == 'index':
                context['deal'] = 'index'
            if deal == 'change_member':
                context['deal'] = 'change_member'
            if deal == 'send_goods':
                context['deal'] = 'send_goods'
                cursor.execute("select * from order_form where send_date = '1900-01-01'")
                send_goods_data = cursor.fetchall()
                context['send_goods_data'] = send_goods_data
            if deal == 'update_order':
                context['deal'] = 'update_order'
                cursor.execute("select order_form.ono,order_form.submit_date,send_date,total_price,mno,order_information.bno, order_number,bname from order_form,order_information,books where order_form.ono=order_information.ono and order_information.bno=books.bno group by order_form.ono,order_form.submit_date,send_date,total_price,mno,order_number,order_information.bno,bname")
                order_informations = cursor.fetchall()#所有数据组成的元组
                # order_onos = [order_information[0] for order_information in order_informations]#订单号作为键值k
                # order_fronts = [order_information[:6] for order_information in order_informations]#前面的重复字段
                context['order_informations'] = dict()#创建一个空的字典来存储订单信息
                for i in order_informations:
                    if context['order_informations'].get(i[0]):#如果订单号的k存在，进行继续添加具体信息即书的数量和种类
                        context['order_informations'][i[0]]['number'] += 1
                        context['order_informations'][i[0]]['books'].append(i[5:8])

                    else:#如果订单号不存在，添加该订单号的第一条数据进入字典
                        context['order_informations'][i[0]] = {
                            'number': 2,#为什么把初始值改成2就渲染成功了
                            'order_front': i[:5],
                            'books': [i[5:8]],
                        }
            if deal == 'update_goods':
                if request.GET.get('bno'):#如果得到查询字符串bno
                    bno = request.GET.get('bno')
                    cursor.execute("select * from books where bno='{}'".format(bno))
                    book_data = cursor.fetchall()[0]
                    context['book_data'] = book_data
                if request.GET.get('books_data_position'):
                    books_data_position = request.GET.get('books_data_position')
                    try:
                        mydf = pd.read_excel(books_data_position, encoding='utf-8')
                        mydf_tuples = [tuple(xi) for xi in mydf.values]#df转元组
                        for mydf_tuple in mydf_tuples:
                            cursor.execute("insert into test_books(bno, bname, category, press, author, survey, price, discount, stock) values {}".format(mydf_tuple))
                        return HttpResponse("批量导入成功")
                    except:
                        return HttpResponse('输入的路径有误或者存在重复导入')
                if request.GET.get('delete_book_ID'):
                    delete_book_ID = request.GET.get('delete_book_ID')
                    cursor.execute("delete from books where bno={}".format(delete_book_ID))
                    return HttpResponse("删除成功")
                context['deal'] = 'update_goods'

        if request.method == 'POST':#post方法
            if deal == 'change_member':
                change_member(request)
                return HttpResponse('修改会员信息成功！')
            if deal == 'send_goods':
                send_goods(request)
                return HttpResponse('发货成功')
            if deal == 'update_order':
                update_order(request)
                return HttpResponse('删除订单信息成功')
            if deal == 'update_goods':
                update_goods(request)
                if request.POST.get('stock') < 0:
                    return HttpResponse('书的数量不能小于0')
                return HttpResponse('更新图书信息成功')



        context['manager_user'] = 'root'#添加验证身份字段，以便渲染页面
        return render(request, 'manager.html', context=context)
    else:
        return HttpResponse("请输入管理员账号密码登录")

def change_member(request):
    account = request.POST.get('account')
    password = request.POST.get('pwd1')
    name = request.POST.get('name')
    telephone = request.POST.get('telephone')
    email = request.POST.get('email')
    address = request.POST.get('address')
    try:
        cursor.execute("update member set mno='{}',mpassword='{}',mname='{}',mphone='{}',mpost='{}',madress='{}' where mno='{}'".format(account, password, name, telephone, email, address, account))
    except:
        pass

def send_goods(request):#管理员发货函数
    ono = request.POST.get('order_ID')
    cursor.execute("update order_form set send_date='{}' where ono='{}'".format(datetime.today(), ono))

def update_order(request):
    ono = request.POST.get('delete_order')
    cursor.execute("delete from order_form where ono='{}'".format(ono))

def update_goods(request):
    web_bno = request.POST.get('bno')
    web_bname = request.POST.get('bname')
    web_category = request.POST.get('category')
    web_press = request.POST.get('press')
    web_author = request.POST.get('author')
    web_survey = request.POST.get('survey')
    web_price = request.POST.get('price')
    web_discount = request.POST.get('discount')
    web_stock = request.POST.get('stock')
    bookdata = cursor.execute("select * from books where bno='{}'".format(web_bno)).fetchone()

    if web_bname == '':#如果获取不到就填补原来的值
        web_bname = bookdata[1]
    if web_category == '':
        web_category = bookdata[2]
    if web_press == '':
        web_press = bookdata[3]
    if web_author == '':
        web_author = bookdata[4]
    if web_survey == '':
        web_survey = bookdata[5]
    if web_price == '':
        web_price = bookdata[6]
    if web_discount == '':
        web_discount = bookdata[7]
    if web_stock == '':
        web_stock = bookdata[8]
    cursor.execute("update books set bname='{}',category='{}', press='{}', author='{}', survey='{}', price='{}', discount='{}', stock='{}' where bno='{}'".format(web_bname, web_category, web_press, web_author, web_survey, web_price, web_discount, web_stock, web_bno))




def logout_manager(request):#退出登录视图
    response = redirect(reverse('home'))
    response.delete_cookie('manager_account')
    return response