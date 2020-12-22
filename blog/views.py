from django.shortcuts import render,get_object_or_404
from .models import Blog, BlogType
from django.core.paginator import Paginator
from django.conf import settings
from django.db.models import Count
from datetime import datetime
from read_statistics.utils import read_statistics_once_read
from django.contrib.contenttypes.models import ContentType


"""    由于comments等都自定义标签后，不再需要了
from comment.models import Comment
from comment.forms import CommentForm
"""

# each_page_blog_number = 2    定义默认分页值

# 获取博客列表共同数据
def get_blog_list_common_data(request, blogs_all_list):
    # 每each_page_blog_number页进行分页
    paginator = Paginator(blogs_all_list, settings.EACH_PAGE_BLOGS_NUMBER)
    # 获取页码参数(GET请求)
    page_num = request.GET.get('page', 1)
    # Django提供的get_page方法：即使得到不是整数类型，也会返回1
    page_of_blogs = paginator.get_page(page_num)

    # 以当前页page_num为中心的前后几页。最后+1是因为页码从0开始
    current_page_num = page_of_blogs.number
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    # 加上省略页码标记。这里放在第一页和最后一页前面的原因：此时的页码范围不是1~17。防止省略号可点，再魔法页面加上判断
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    # 添加第一页和最后一页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    '''
    获取博客分类对应的数量 方法一
    blog_types = BlogType.objects.all()
    blog_types_list = []
    for blog_type in blog_types:
        # filter(参数=参数值)
        blog_type.blog_count = Blog.objects.filter(blog_type = blog_type).count()
        blog_types_list.append(blog_type)    由于blog_type.blog_count是临时的，所以创建blog_types_list列表存储
    '''

    # 获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
    blog_date_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year, created_time__month=blog_date.month).count()
        blog_date_dict[blog_date] = blog_count

    context = {}
    context['blogs'] = page_of_blogs.object_list    # 获取分页内容
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range    # 给魔法页面传递页码范围

    # context['blog_count'] = Blog.objects.all().count()    返回博客数量

    # 返回所有博客类型
    # 方法一：context['blog_types'] = blog_types_list
    # 方法二 annotate注释。注释信息加上统计，统计每一条查询结果的分类对应有多少条博客。需要导入django.db.models里Count统计方法。Count('blog_blog')
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))

    # dates(field字段，kind类型，order排序)，返回一个提供可用日期的查询（QuerySet）
    # context['blog_dates'] = Blog.objects.dates('created_time', 'month', order="DESC")
    context['blog_dates'] = blog_date_dict    # 此时传给魔法页面的是字典，而不是查询QuerySet。所以需要修改魔法页面

    return context

# blog列表
def blog_list(request):
    blogs_all_list = Blog.objects.all()    # 获取全部博客
    context = get_blog_list_common_data(request, blogs_all_list)
    return render(request, 'blog/blog_list.html', context)

# blog类型
def blogs_with_type(request,blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk = blog_type_pk)    # 打开具体某篇博客
    blogs_all_list = Blog.objects.filter(blog_type = blog_type)

    context = get_blog_list_common_data(request, blogs_all_list)
    context['blog_type'] = blog_type

    return render(request, 'blog/blogs_with_type.html', context)

# 按照日期的分类方法
def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blog_list_common_data(request, blogs_all_list)
    context['blogs_with_date'] = '%s年%s月' % (year, month)    # 给blog_with_date.html传递年月信息

    return render(request, 'blog/blogs_with_date.html', context)

# 显示具体的blog页面,主键primary key(pk)是每个Django模型对象自带的属性。有时候主键字段不一定叫id
def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, id=blog_pk)    # 获取具体的blog模型

    read_cookie_key = read_statistics_once_read(request, blog)
    ''' 阅读计数 判断cookie是否存在此键值，不存在再加1
   if not request.COOKIES.get('blog_%s_read' % blog_pk):
       方法一
       blog.read_num += 1
       blog.save()
       
       方法二
       if ReadNum.objects.filter(blog=blog).count():    # 存在记录
           readnum = ReadNum.objects.get(blog=blog)    # 获得阅读数
       else:
           readnum = ReadNum(blog=blog)    # 创建阅读记录
       readnum.read_num += 1    # 计数加一
       readnum.save()
   '''

    """
    blog_content_type = ContentType.objects.get_for_model(blog)    # 获取blog的content_type类型
    这句话由于comments等都自定义标签后，不再需要了
    
    通过comment_tags将comments自定义标签后删除
    # 通过筛选得到该博客的类型，和主键值。显示1级评论并将其parent设置为None
    comments = Comment.objects.filter(content_type=blog_content_type, object_id=blog.pk, parent=None)
    """

    context = {}
    # 上一篇博客（比较类型参数=参数值），会得到所有比当前时间大的博客；last是查询到博客的最后一条，博客顺序是倒序
    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last
    # 下一条博客 切片(...)[0]也可以
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first
    context['blog'] = blog

    # context['login_form'] = LoginForm()    模态框弹出登录  为form写公共魔法变量后删除

    """
    通过comment_tags将comments自定义标签后删除
    context['comments'] = comments.order_by('-comment_time')    # 将comments返回给魔法页面，将一级评论倒叙排列
    """

    # context['user'] = request.user    返回用户状态给魔法页面，供其判断是否登录。使用render则不需要

    """
    data = {} # data字典，有两个参数content_type和object_id
    data['content_type'] = blog_content_type.model    # 初始化为blog_content_type对象里的字符串model
    data['object_id'] = blog_pk
    context['comment_form'] = CommentForm(initial=data)    # 实例化form后传递给blog_detail魔法页面。初始化时赋予默认值data
    """
    """
    通过comment_tags将comment_form自定义标签后删除
    # 初始化参数不多，可以简写。如果是1级评论，所以将reply_comment_id初始化为0
    context['comment_form'] = CommentForm(initial={'content_type':blog_content_type.model, 'object_id': blog_pk, 'reply_comment_id': '0'})
    """

    response = render(request, 'blog/blog_detail.html', context)    # 响应
    # set_cookie(key, value, max_age=时效性, expires=datetime 这两个参数冲突，两个都不设置退出浏览器cookie才会失效)：让浏览器保存相关数据
    # response.set_cookie('blog_%s_read' % blog_pk, 'true')    方法二
    response.set_cookie(read_cookie_key, 'true')    # 方法三 阅读cookie标记
    return response

