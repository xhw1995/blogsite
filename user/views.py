import string
import random
import time
from django.shortcuts import render, redirect
from django.contrib import auth
from django.urls import reverse
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.core.mail import send_mail
from .forms import LoginForm, RegForm, ChangeNicknameForm, BindEmailForm, ChangePasswordForm, ForgotPasswordForm
from .models import Profile

def login_for_model(request):  # 模态框登录方法
    login_form = LoginForm(request.POST)  # 如果是POST提交数据，将提交的数据初始化
    data = {}

    if login_form.is_valid():  # 验证通过
        user = login_form.cleaned_data['user']
        auth.login(request, user)
        data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def login(request):
    """
    使用Django Form后删除下面代码
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = auth.authenticate(request, username=username, password=password)
    referer = request.META.get('HTTP_REFERER', reverse('home'))    # 请求头包含从哪个页面进来的信息。获取当前页面网址，登录后跳转到该网址。获取不到通过别名反向解析获得链接
    if user is not None:
        auth.login(request, user)
        return redirect(referer)    # 登录成功，返回首页'/'。从请求头获取当前页面网址，跳转到当前页面
    else:
        return render(request, 'error.html', {'message':'用户名或密码不正确'})
    """

    if request.method == 'POST':
        login_form = LoginForm(request.POST)  # 如果是POST提交数据，将提交的数据初始化
        if login_form.is_valid():  # 验证通过
            user = login_form.cleaned_data['user']
            auth.login(request, user)
            # 这里不是跳转当前页面(登录页面)，而是跳转到前一个页面。在blog_detail中通过request.get_full_path获取全部信息，没有则反向跳到首页
            return redirect(request.GET.get('from', reverse('home')))
            """    将验证修改到forms.py时删除下面代码
            username = login_form.cleaned_data['username']    # cleaned_data是字典，包含所需字段信息。是验证后整理过的信息，可直接使用
            password = login_form.cleaned_data['password']
            user = auth.authenticate(request, username=username, password=password)    # 登录操作
            if user is not None:

                auth.login(request, user)
                # 这里不是跳转当前页面(登录页面)，而是跳转到前一个页面。在blog_detail中通过request.get_full_path获取全部信息，没有则反向跳到首页
                return redirect(request.GET.get('from', reverse('home')))
            else:
                login_form.add_error(None, '用户名或密码不正确')    # 将错误添加到form的错误集中，后面的form就会携带该信息
            """
    else:
        login_form = LoginForm()  # 实例化LoginForm类
    context = {}
    context['login_form'] = login_form  # 传递给login.html魔法页面
    return render(request, 'user/login.html', context)    # 修改魔法页面路径

def register(request):
    if request.method == 'POST':
        reg_form = RegForm(request.POST, request=request)  # 如果是POST提交数据，将提交的数据初始化
        if reg_form.is_valid():
            username = reg_form.cleaned_data['username']
            email = reg_form.cleaned_data['email']
            password = reg_form.cleaned_data['password']
            user = User.objects.create_user(username, email, password)  # 通过导入User模块创建用户
            """
            创建一个实例化对象注册也可以
            user = User()
            user.username = username
            user.email = email
            user.set_password(password)
            """
            user.save()
            # 清除session，防止用一个验证码多次注册
            del request.session['register_code']

            # 登录用户
            user = auth.authenticate(username=username, password=password)
            auth.login(request, user)
            return redirect(request.GET.get('from', reverse('home')))  # 登陆后跳转到执行注册页面的路径
    else:
        reg_form = RegForm()  # 实例化LoginForm类
    context = {}
    context['reg_form'] = reg_form  # 传递给login.html魔法页面
    return render(request, 'user/register.html', context)

def logout(request):
    auth.logout(request)
    return redirect(request.GET.get('from', reverse('home')))  # 退出后跳转到当前页面

def user_info(request):
    context = {}
    return render(request, 'user/user_info.html', context)  # 返回用户信息魔法页面

def change_nickname(request):
    redirect_to = request.GET.get('form', reverse('home'))    # 返回地址，没有则返回首页

    if request.method == 'POST':    # 判断是POST请求还是GET请求
        form = ChangeNicknameForm(request.POST, user=request.user)
        if form.is_valid():    # 验证通过
            nickname_new = form.cleaned_data['nickname_new']
            profile, created = Profile.objects.get_or_create(user=request.user)    # 如果原本没有昵称，则创建昵称
            profile.nickname = nickname_new
            profile.save()
            return redirect(redirect_to)
    else:
        form = ChangeNicknameForm()

    context = {}
    context['page_title'] = '修改昵称'
    context['form_title'] = '修改昵称'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_url'] = redirect_to    # 返回按钮返回地址
    return render(request, 'form.html', context)    # 这里使用公共魔法页面渲染

def bind_email(request):
    redirect_to = request.GET.get('form', reverse('home'))  # 返回地址，没有则返回首页

    if request.method == 'POST':  # 判断是POST请求还是GET请求
        form = BindEmailForm(request.POST, request=request)
        if form.is_valid():    # 验证通过，绑定邮箱
            email = form.cleaned_data['email']
            request.user.email = email
            request.user.save()
            # 清除session，防止用一个验证码多次注册
            del request.session['bind_email_code']
            return redirect(redirect_to)
    else:
        form = BindEmailForm()

    context = {}
    context['page_title'] = '绑定邮箱'
    context['form_title'] = '绑定邮箱'
    context['submit_text'] = '绑定'
    context['form'] = form
    context['return_back_url'] = redirect_to  # 返回按钮返回地址
    return render(request, 'user/bind_email.html', context)  # 这里使用公共魔法页面渲染

def send_verification_code(request):    # 发用验证码的方法
    email = request.GET.get('email', '')
    send_for = request.GET.get('send_for', '')
    data = {}    # 用于存储发送是否成功的状态

    if email != '':
        # 生成验证码
        code = ''.join(random.sample(string.ascii_letters + string.digits, 4))    # 大小写英文字母和数字随机组成4位验证码，join是变成字符串
        now = int(time.time())    # 当前时间
        send_code_time = request.session.get('bind_email_time', 0)    # 记录生成验证码的时间
        if now - send_code_time < 60:    # 判读用户发送验证码是否过了60s
            data['status'] = 'ERROR'
        else:
            request.session[send_for] = code    # 用数据库的session保存验证码，用于后续验证，有效期为两周（可更改）。也可以存在cookie中
            request.session['send_code_time'] = now    # 保存用户发送验证码的时间，不让其短时间内多次发送

            # 发送邮件
            send_mail(
                '绑定邮箱',  # 主题
                '验证码：%s' % code,  # 验证码
                '562193521@qq.com',  # 发送邮箱
                [email],  # 目标邮箱
                fail_silently=False,  # 是否忽略错误
            )
            data['status'] = 'SUCCESS'
    else:
        data['status'] = 'ERROR'
    return JsonResponse(data)

def change_password(request):
    redirect_to = reverse('home')
    if request.method == 'POST':  # 判断是POST请求还是GET请求
        form = ChangePasswordForm(request.POST, user=request.user)
        if form.is_valid():  # 验证通过
            user = request.user
            old_password = form.cleaned_data['old_password']
            new_password = form.cleaned_data['new_password']
            user.set_password(new_password)    # 修改密码用set_password
            user.save()
            auth.logout(request)    # 修改后登出
            return redirect(redirect_to)
    else:
        form = ChangePasswordForm()

    context = {}
    context['page_title'] = '修改密码'
    context['form_title'] = '修改密码'
    context['submit_text'] = '修改'
    context['form'] = form
    context['return_back_url'] = redirect_to  # 返回按钮返回地址
    return render(request, 'form.html', context)  # 这里使用公共魔法页面渲染

def forgot_password(request):
    redirect_to = reverse('login')    # 返回登录页面

    if request.method == 'POST':  # 判断是POST请求还是GET请求
        form = ForgotPasswordForm(request.POST, request=request)
        if form.is_valid():  # 验证通过，重置密码
            email = form.cleaned_data['email']
            new_password = form.cleaned_data['new_password']
            user = User.objects.get(email=email)
            user.set_password(new_password)
            user.save()

            # 清除session中的忘记密码
            del request.session['forgot_password_code']
            return redirect(redirect_to)
    else:
        form = ForgotPasswordForm()

    context = {}
    context['page_title'] = '重置密码'
    context['form_title'] = '重置密码'
    context['submit_text'] = '重置'
    context['form'] = form
    context['return_back_url'] = redirect_to  # 返回按钮返回地址
    return render(request, 'user/forgot_password.html', context)  # 这里使用公共魔法页面渲染