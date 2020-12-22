from django.urls import path
from . import views

urlpatterns = [
    path('login_for_model/', views.login_for_model, name='login_for_model'),  # 模态框登录路由
    path('login/', views.login, name='login'),  # 登录路由
    path('register/', views.register, name='register'),  # 注册路由
    path('logout/', views.logout, name='logout'),  # 退出路由
    path('user_info/', views.user_info, name='user_info'),  # 用户信息路由
    path('change_nickname/', views.change_nickname, name='change_nickname'),    # 修改昵称路由
    path('bind_email/', views.bind_email, name='bind_email'),    # 绑定邮箱路由
    path('send_verification_code/', views.send_verification_code, name='send_verification_code'),    # 验证码路由
    path('change_password/', views.change_password, name='change_password'),    # 修改密码路由
    path('forgot_password/', views.forgot_password, name='forgot_password'),    # 忘记密码路由
]