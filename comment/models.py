import threading
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render

# 多线程，异步处理发送邮件
class SendMail(threading.Thread):
    def __init__(self, subject, text, email, fail_silently=False):    # 初始化时传入参数
        self.subject = subject
        self.text = text
        self.email = email
        self.fail_silently = fail_silently
        threading.Thread.__init__(self)

    def run(self):
        send_mail(
            self.subject,
            '',
            settings.EMAIL_HOST_USER,
            [self.email],
            fail_silently=self.fail_silently,
            html_message=self.text    # html邮件
        )

class Comment(models.Model):
    # 被评论对象信息
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')  # 将content_type和object_id统一变成通用的外键

    text = models.TextField()
    comment_time = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, related_name="comments", on_delete=models.CASCADE)    # 评论是谁写的。related_name是反向解析名称
    # 外键是双向的，即comment可以访问user，user也可以访问comment。如果不写反向解析名称，且有两个外键都指向user，这时就不知道该返回给谁

    # 评论回复字段
    # 获取一条评论下面所有的回复，related_name="+"表示不创建反向关系
    root = models.ForeignKey('self', related_name="root_comment", null=True, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', related_name="parent_comment", null=True, on_delete=models.CASCADE)    # 主键指向自己，允许为空
    reply_to = models.ForeignKey(User, related_name="replies", null=True, on_delete=models.CASCADE)    # 评论是回复谁的

    def send_mail(self):
        if self.parent is None:  # 判断评论是否有parent，没有表示是一级评论
            # 评论博客，发送邮件
            subject = '有人评论你的博客'  # 主题
            email = self.content_object.get_email()  # 评论博客的email
        else:
            # 回复评论
            subject = '有人回复你的评论'  # 主题
            email = self.reply_to.email  # 评论的email
        if email != '':
            # text = self.text + '\n' + self.content_object.get_url()  # 评论内容 + 通过comment.content_object（具体评论的对象）获得url
            context = {}    # 给魔法页面传入内容
            context['comment_text'] = self.text
            context['url'] = self.content_object.get_url()
            text = render(None, 'comment/send_mail.html', context).content.decode('utf-8')

            send_mail = SendMail(subject, text, email)    # 参数传给多线程
            send_mail.start()    # 开始多线程

    def __str__(self):
        return self.text

    # 排序设置，-comment_time倒序排序。设置回复后，将其改为正序
    class Meta:
        ordering = ['comment_time']
