from django.db import models
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericRelation
from ckeditor_uploader.fields import RichTextUploadingField
from django.db.models.fields import exceptions
from read_statistics.models import ReadNumExpandMethod, ReadDetail
from django.urls import reverse

class BlogType(models.Model):
    type_name = models.CharField(max_length=15)

    # 定义这个类如何展示
    def __str__(self):
        return self.type_name

class Blog(models.Model, ReadNumExpandMethod):
    title = models.CharField(max_length=50)

    # 这里暂时使用一篇博文对应一种类型
    # blog_type是外键，要关联到BlogType。
    # 可以定义参数related_name='blog_blog'与BlogType.objects.annotate关联
    blog_type = models.ForeignKey(BlogType, on_delete=models.CASCADE)

    content = RichTextUploadingField()    # content = models.TextField()    替换成富文本类型
    author = models.ForeignKey(User, on_delete=models.CASCADE)     # 作者 使用外键，默认值暂时不写
    read_details = GenericRelation(ReadDetail)    # 为了让get_7_days_hot_data中的read_details能得到响应的数据
    created_time = models.DateTimeField(auto_now_add=True)
    last_update_time = models.DateTimeField(auto_now=True)

    ''' 阅读计数方法二
    # 显示具体的属性或方法，可以添加方法，返回readnum对象里的read_num字段
    def get_read_num(self):
        try:
            return self.readnum.read_num
        except exceptions.ObjectDoesNotExist:    # 导入exceptions，如果发生不存在异常，返回0
            return 0
    '''

    # 得到博客链接
    def get_url(self):
        return reverse('blog_detail', kwargs={'blog_pk': self.pk})

    # 得到评论对象的email
    def get_email(self):
        return self.author.email

    def __str__(self):
        return "<Blog: %s>" % self.title

    # 定义排序规则用于分页，这里采用创建时间倒叙
    class Meta:
        ordering = ['-created_time']

''' 
阅读计数方法二
class ReadNum(models.Model):
    read_num = models.IntegerField(default=0)    # 阅读计数，默认值设为0
    blog = models.OneToOneField(Blog, on_delete=models.CASCADE)    # 这里使用一对一关系字段
'''