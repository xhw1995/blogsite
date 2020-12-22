from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse
from .models import Comment
from .forms import CommentForm
from django.http import JsonResponse

def update_comment(request):
    referer = request.META.get('HTTP_REFERER', reverse('home'))  # 请求头包含从哪个页面进来的信息。获取当前页面网址，登录后跳转到该网址。获取不到通过别名反向解析获得链接

    """    使用django form 后删除
    # 数据检查
    if not request.user.is_authenticated:     # 判断用户是否登录
        return render(request, 'error.html', {'message': '用户未登录', 'redirect_to': referer})

    text = request.POST.get('text', '').strip()    # 获取不到给空''，strip()可以将前后空格去掉
    if text == '':
        return render(request, 'error.html', {'message': '评论内容为空', 'redirect_to': referer})

    try:
        content_type = request.POST.get('content_type', '')
        object_id = int(request.POST.get('object_id', ''))    # 得到的是字符串，需要转成int型
        model_class = ContentType.objects.get(model=content_type).model_class()    # 得到博客content_type的类型，通过model_class得到具体的模型class
        model_obj = model_class.objects.get(pk=object_id)    # 通过model_class得到具体的对象
    except Exception as e:
        return render(request, 'error.html', {'message': '评论对象不存在', 'redirect_to': referer})

    # 检查通过，保存数据
    comment = Comment()
    comment.user = request.user
    comment.text = text
    # Blog.objects.get(pk=object_id)    获取博客对应的记录，但这里没有Blog模型，可以引用Blog。但这里使用ContentType方法
    comment.content_object = model_obj
    comment.save()

    return redirect(referer)
    """

    comment_form = CommentForm(request.POST, user=request.user)    # 使用request.POST实例化一个对象。把user传给form
    data = {}

    if comment_form.is_valid():
        # 检查通过，保存数据
        comment = Comment()
        comment.user = comment_form.cleaned_data['user']
        comment.text = comment_form.cleaned_data['text']
        comment.content_object = comment_form.cleaned_data['content_object']

        # 判断是不是回复
        parent = comment_form.cleaned_data['parent']
        if not parent is None:    # 是回复
            # 判断评论等级，如果parent.root不是None就不是一级评论，填入parent.root；否则填入parent
            # 从前端接收的parent如果不是None，把root属性给它的孩子回复。如果是空，就把自己给孩子的回复
            comment.root = parent.root if not parent.root is None else parent
            comment.parent = parent
            comment.reply_to = parent.user
        comment.save()

        # 评论保存后，发送邮件通知
        """
        if comment.parent is None:    # 判断评论是否有parent，没有表示是一级评论
            # 评论博客，发送邮件
            subject = '有人评论你的博客'    # 主题
            email = comment.content_object.get_email()    # 评论博客的email
        else:
            # 回复评论
            subject = '有人回复你的评论'  # 主题
            email = comment.reply_to.email  # 评论的email
        if email != '':
            text = comment.text + '\n' + comment.content_object.get_url()  # 评论内容 + 通过comment.content_object（具体评论的对象）获得url
            send_mail(subject, text, settings.EMAIL_HOST_USER, [email], fail_silently=False)
        """
        comment.send_mail()

        # return redirect(referer) 使用ajax异步请求后删除
        # 返回数据
        data['status'] = 'SUCCESS'
        data['username'] = comment.user.get_nickname_or_username()    # 注意：这里需要()，魔法页面的方法不需要()
        data['comment_time'] = comment.comment_time.timestamp()    # 使用时间戳，返回数字给前端页面
        data['text'] = comment.text
        data['content_type'] = ContentType.objects.get_for_model(comment).model

        # 判断是不是回复，返回一些数据
        if not parent is None:
            data['reply_to'] = comment.reply_to.get_nickname_or_username()    # 非回复情况，返回回复给谁(昵称或者用户名)
        else:
            data['reply_to'] = ''    # 不是，则返回空
        data['pk'] = comment.pk
        data['root_pk'] = comment.root.pk if not comment.root is None else ''

    else:
        # return render(request, 'error.html', {'message': comment_form.errors, 'redirect_to': referer}) 使用ajax异步请求后删除
        data['status'] = 'ERROR'
        data['message'] = list(comment_form.errors.values())[0][0]
    return JsonResponse(data)
