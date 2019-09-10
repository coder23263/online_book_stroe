from django.shortcuts import render
from django.http import HttpResponse
from shopping.views import shopping_cart
from datetime import datetime
from django.db import connection
import time


def get_cursor():
    return connection.cursor()

def member(request):
    return HttpResponse("会员")

def shop_cart(request):#购物车视图函数
    cookies = request.COOKIES

    if cookies.get('account'):
        account = request.GET.get("account")
        global shopping_cart
        if request.method == 'POST':
            if request.POST.get("book_plus"):
                shopping_cart[request.POST.get("book_plus")] += 1

            elif request.POST.get("book_reduce"):
                shopping_cart[request.POST.get("book_reduce")] -= 1
                if shopping_cart[request.POST.get("book_reduce")] == 0:  # 如果数量为零就移除购物车中该商品
                    shopping_cart.pop(request.POST.get("book_reduce"))

            elif request.POST.get("create_order"):#提交订单函数
                cursor = get_cursor()
                for key, value in shopping_cart.items():
                    if cursor.execute("select stock from books where bno='{}'".format(key)).fetchone()[0] < value:
                        #shopping_cart.clear()  # 清空购物车
                        return HttpResponse("{}库存不足,请查看库存从新选择并提交订单".format(key))

                ono = str(request.GET.get("account")) + "_" + str(int(time.time()))#获取账户名加空格加时间戳W为订单唯一ID

                total_price = 0#用来存放订单总价
                for key, value in shopping_cart.items():
                    price_and_discount = cursor.execute("select price, discount from books where bno='{}'".format(key)).fetchone()
                    price = price_and_discount[0]
                    discount = price_and_discount[1]
                    total_price += price * discount * value * 0.1#计算订单总价

                ####     插入操作,将订单信息插入order_form,    #####
                cursor.execute("insert into order_form(ono, submit_date, send_date, total_price, mno) values('{}','{}','{}','{:.2f}','{}')".format(ono, datetime.today(), '', total_price, account))
                #将订购信息插入order_information ,订单号，书号，书的数量，因为有主键约束，所有先进行插入order_form，后进行插入order_information
                for key, value in shopping_cart.items():
                    cursor.execute("insert into order_information(bno, ono, order_number) values('{}','{}','{}')".format(key, ono,value))
                #将订单图书在库存中减少
                for key, value in shopping_cart.items():
                    orig_stock = cursor.execute("select stock from books where bno='{}'".format(key)).fetchone()[0]
                    cursor.execute("update books set stock='{}' where bno='{}'".format(orig_stock - value, key))
                #订单提交到数据库，清空购物车字典
                shopping_cart.clear()#清空购物车
                return HttpResponse("订单提交成功")
            else:
                print("另类的post请求")
        context = {
            'account': account,#暂时没有用到
            'books': shopping_cart,

        }
        #print(context)
        return render(request, 'shopping_cart.html', context=context)
    else:
        return HttpResponse("请登录后查看购物车")
