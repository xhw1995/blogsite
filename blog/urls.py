from django.urls import path
from . import views

urlpatterns = [
    # 参数：不写就是博客列表；处理方法；别名。这样就定义好博客列表的链接，即下面网址
    path('', views.blog_list, name='blog_list'),

    # 网址格式：http://localhost:8000/blog/
    # 参数：对应的具体文章需要int整数变量；处理方法；别名
    path('<int:blog_pk>', views.blog_detail, name="blog_detail"),
    # 如果不加type/，就会由于传入的两个都是数字而先传入第一条路由出现错误
    path('type/<int:blog_type_pk>', views.blogs_with_type, name='blogs_with_type'),
    # 按照日期的分类。路由，处理方法，别名
    path('date/<int:year>/<int:month>', views.blogs_with_date, name="blogs_with_date"),
]
