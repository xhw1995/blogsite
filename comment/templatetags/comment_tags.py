from django import template
from django.contrib.contenttypes.models import ContentType
from ..models import Comment    # ..表示上一层文件夹
from ..forms import CommentForm

register = template.Library()    # 用于注册

@register.simple_tag    # 将方法注册
def get_comment_count(obj):
    content_type = ContentType.objects.get_for_model(obj)    # 通过具体对象得到content_type
    return Comment.objects.filter(content_type=content_type, object_id=obj.pk).count()

@register.simple_tag
def get_comment_form(obj):
    content_type = ContentType.objects.get_for_model(obj)
    form = CommentForm(initial={'content_type': content_type.model, 'object_id': obj.pk, 'reply_comment_id': '0'})
    return form

@register.simple_tag
def get_comment_list(obj):
    content_type = ContentType.objects.get_for_model(obj)
    comments = Comment.objects.filter(content_type=content_type, object_id=obj.pk, parent=None)
    return comments.order_by('-comment_time')