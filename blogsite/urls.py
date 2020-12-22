"""blogsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

# 在不同目录下的引用可能会出现错误，但是可以正常运行。修改主页路径后，不再需要
# from blog.views import blog_list

from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.home, name='home'),    # 首页
    path('admin/', admin.site.urls),
    path('ckeditor', include('ckeditor_uploader.urls')),    # 配置上传路由
    path('blog/', include('blog.urls')),    # 博客app路由
    path('comment/', include('comment.urls')),    # 评论app路由
    path('likes/', include('likes.urls')),    # 点赞app路由
    path('user/', include('user.urls')),    # user app的路由
]

# 设置路由可以访问media文件夹下的目录
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
