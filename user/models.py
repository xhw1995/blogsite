from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)    # 一个User对应一个Profile
    nickname = models.CharField(max_length=20, verbose_name='昵称')    # 昵称

    def __str__(self):
        return '<Profile: %s for %s>' % (self.nickname, self.user.username)    # 显示昵称和用户名

def get_nickname(self):    # 下滑导航栏显示昵称
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return ''

def get_nickname_or_username(self):    # 评论显示：有昵称显示昵称，没有则显示用户名
    if Profile.objects.filter(user=self).exists():
        profile = Profile.objects.get(user=self)
        return profile.nickname
    else:
        return self.username

def has_nickname(self):
    return Profile.objects.filter(user=self).exists()

User.get_nickname = get_nickname    # 动态绑定：将get_nickname的值赋给User的自定义参数get_nickname，再传给user_info.html
User.has_nickname = has_nickname
User.get_nickname_or_username = get_nickname_or_username