from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

class LikeCount(models.Model):
    # 被点赞对象信息
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')  # 将content_type和object_id统一变成通用的外键

    liked_num = models.IntegerField(default=0)

class LikeRecord(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')  # 将content_type和object_id统一变成通用的外键

    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 评论是谁写的。
    liked_time = models.DateTimeField(auto_now_add=True)    # 点赞时间
