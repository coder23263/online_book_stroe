from django.db import connection


def front_user(request):
    cookies = request.COOKIES
    account = cookies.get('account')
    context = {}
    if account:
        cursor = connection.cursor()
        cursor.execute("select * from MEMBER where mno={}".format(account))  # 获取昵称
        name = cursor.fetchone()[2]
        # print("=" * 15)
        # print(account, name)
        # print("=" * 15)
        try:
            context['front_user'] = account
            context['name'] = name
        except:
            pass
    return context