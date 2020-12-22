from django import forms
from django.contrib.contenttypes.models import ContentType
from django.db.models import ObjectDoesNotExist
from ckeditor.widgets import CKEditorWidget
from .models import Comment

class CommentForm(forms.Form):
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_id = forms.IntegerField(widget=forms.HiddenInput)
    text = forms.CharField(widget=CKEditorWidget(config_name='comment_ckeditor'),
                           error_messages={'required': '评论内容不能为空'})    # 富文本编辑框，具体设置写在settings中的CKEDITOR_CONFIGS里

    # 回复对应评论的主键值：数字类型，不需要给用户看，设置一个属性(id)值通过前端页面获取，设置id值为reply_comment_id
    reply_comment_id = forms.IntegerField(widget=forms.HiddenInput(attrs={'id': 'reply_comment_id'}))

    def __init__(self, *args, **kwargs):    # 任意类型参数，任意关键字参数
        if 'user' in kwargs:
            self.user = kwargs.pop('user')   # 接收comment/views传递的user，收到后抛出。self可以让其在别的地方使用
        super(CommentForm, self).__init__(*args, **kwargs)

    # views下的blog_detail()方法主体是blog，它有POST请求页面，为了防止冲突，将表单处理逻辑放在这里
    def clean(self):
        # 判断用户是否登录 这里的user是__init__从views那接收的，不接收则没有
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')

        # 评论对象验证
        content_type = self.cleaned_data['content_type']
        object_id = self.cleaned_data['object_id']
        try:
            model_class = ContentType.objects.get(model=content_type).model_class()
            model_obj = model_class.objects.get(pk=object_id)
            self.cleaned_data['content_object'] = model_obj
        except ObjectDoesNotExist:
            raise forms.ValidationError('评论对象不存在')
        return self.cleaned_data

    # 验证reply_comment_id字段数据
    def clean_reply_comment_id(self):
        reply_comment_id = self.cleaned_data['reply_comment_id']
        if reply_comment_id < 0:    # 小于0，不存在
            raise forms.ValidationError('回复出错')
        elif reply_comment_id == 0:    # 等于0，表示该评论是一级评论
            self.cleaned_data['parent'] = None
        elif Comment.objects.filter(pk=reply_comment_id).exists():    # 大于0，要判断其在数据库是否存在
            self.cleaned_data['parent'] = Comment.objects.get(pk=reply_comment_id)    # 存在则返回那条评论
        else:    # 找不到数据
            raise forms.ValidationError('回复出错')
        return reply_comment_id