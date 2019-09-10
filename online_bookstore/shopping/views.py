from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
import re

#为购物车定义一个字典，字段为： 书的ID：数量
shopping_cart = dict()


def get_cursor():
    return connection.cursor()


def index(request):
    cursor = get_cursor()
    cursor.execute("SELECT * FROM BOOKS")
    rows = cursor.fetchall() #get到所有元组组成的集合
    #print(rows)

    if request.method == 'GET':
        if request.GET.get('category'):
            new_rows = []
            for row in rows:
                if request.GET.get('category') in row[0]:
                    new_rows.append(row)
            context = {
                'books': new_rows,
            }
            return render(request, 'shopping.html', context=context)

    context = {
        'books': rows,
    }
    #如果表单提交为post请求，添加书到购物车（因为刚刷新页面的时候有一次空值，要忽略这次空值）
    if request.method == 'POST' and request.POST.get("book") is not None:
        add_shopping_cart(request.POST.get("book"))#执行加入购物车函数，传参为商品ID
    return render(request, 'shopping.html', context=context)


def add_shopping_cart(bno):#传入的参数是bno即书的ID
    global shopping_cart
    if shopping_cart.get(bno):#若存在数量加一，不存在就置1
        shopping_cart[bno] += 1
    else:
        shopping_cart[bno] = 1
