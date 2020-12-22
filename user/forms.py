from django import forms
from django.contrib import auth
from django.contrib.auth.models import User

class LoginForm(forms.Form):
    # 默认要求填写为True
    username_or_email = forms.CharField(label='用户名或邮箱', required=True,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入用户名或邮箱'}))
    # widget定义input标签最终为什么样子，是一个类可以实例化
    password = forms.CharField(label='密码',
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}))

    def clean(self):    # 验证登录
        username_or_email = self.cleaned_data['username_or_email']
        password = self.cleaned_data['password']
        user = auth.authenticate(username=username_or_email, password=password)  # 登录操作
        if user is None:    # 通过邮箱或第三方登录时，判断用户是否存在
            if User.objects.filter(email=username_or_email).exists():
                username = User.objects.get(email=username_or_email).username
                user = auth.authenticate(username=username, password=password)  # 登录操作
                if not user is None:
                    self.cleaned_data['user'] = user
                    return self.cleaned_data
            raise forms.ValidationError('用户名或密码不正确')
        else:
            self.cleaned_data['user'] = user    # 将验证后的user写入cleaned_data
        return self.cleaned_data

# 注册类
class RegForm(forms.Form):
    username = forms.CharField(label='用户名', required=True, max_length=30, min_length=3,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入3-30位用户名'}))
    email = forms.EmailField(label='邮箱', required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入邮箱地址'}))
    password = forms.CharField(label='密码', min_length=8,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入密码'}))
    password_again = forms.CharField(label='再输入一次密码', min_length=8,
                                     widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '再输入一次密码'}))
    verification_code = forms.CharField(label='验证码', required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(RegForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断验证码
        code = self.request.session.get('register_code', '')  # 注册生成的验证码
        verification_code = self.cleaned_data.get('verification_code', '')  # 用户填写的验证码
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码错误')
        return self.cleaned_data

    def clean_username(self):    # 针对用户名验证
        username = self.cleaned_data['username']
        # 通过导入User模型判断用户名是否重复
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError('用户名已存在')
        return username

    def clean_email(self):    # 针对邮箱验证
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已存在')
        return email

    def clean_password_again(self):    # 针对密码验证
        password = self.cleaned_data['password']
        password_again = self.cleaned_data['password_again']
        if password != password_again:
            raise forms.ValidationError('两次输入的密码不一致')
        return password_again

    def clean_verification_code(self):    # 针对验证码验证
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code

# 修改昵称
class ChangeNicknameForm(forms.Form):
    nickname_new  =forms.CharField(label='新的昵称', max_length=20,
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '请输入新的昵称'}))

    def __init__(self, *args, **kwargs):    # 任意类型参数，任意关键字参数
        if 'user' in kwargs:
            self.user = kwargs.pop('user')   # 接收comment/views传递的user，收到后抛出。self可以让其在别的地方使用
        super(ChangeNicknameForm, self).__init__(*args, **kwargs)

    # views下的blog_detail()方法主体是blog，它有POST请求页面，为了防止冲突，将表单处理逻辑放在这里
    def clean(self):
        # 判断用户是否登录 这里的user是__init__从views那接收的，不接收则没有
        if self.user.is_authenticated:
            self.cleaned_data['user'] = self.user
        else:
            raise forms.ValidationError('用户尚未登录')
        return self.cleaned_data

    def clean_nickname_new(self):    # 判断昵称是否合法
        nickname_new = self.cleaned_data.get('nickname_new').strip()    # strip将字符串前后空格去掉
        if nickname_new == '':
            raise forms.ValidationError('新的昵称不能为空')
        return nickname_new

# 绑定邮箱
class BindEmailForm(forms.Form):
    email = forms.EmailField(label='邮箱',
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入正确的邮箱'}))
    verification_code = forms.CharField(label='验证码', required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}))

    def __init__(self, *args, **kwargs):
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(BindEmailForm, self).__init__(*args, **kwargs)

    def clean(self):
        # 判断用户是否登录
        if self.request.user.is_authenticated:
            self.cleaned_data['user'] = self.request.user
        else:
            raise forms.ValidationError('用户尚未登录')

        # 判断用户是否已绑定邮箱
        if self.request.user.email != '':
            raise forms.ValidationError('已绑定邮箱')

        # 判断验证码
        code = self.request.session.get('bind_email_code', '')    # 生成的验证码
        verification_code = self.cleaned_data.get('verification_code', '')    # 用户填写的验证码
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码错误')

        return self.cleaned_data

    def clean_email(self):    # 验证邮箱是否重复
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱已被绑定')
        return email

    def clean_verification_code(self):
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')
        return verification_code

# 修改密码
class ChangePasswordForm(forms.Form):
    old_password = forms.CharField(label='旧密码',
                                   widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入旧密码'}))
    new_password = forms.CharField(label='新密码',
                                   widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入新密码'}))
    new_password_again = forms.CharField(label='验证新密码',
                                         widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请在输入一次新密码'}))

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super(ChangePasswordForm, self).__init__(*args, **kwargs)

    # 验证新的密码是否一致
    def clean(self):
        new_password = self.cleaned_data.get('new_password', '')
        new_password_again = self.cleaned_data.get('new_password_again', '')
        if new_password != new_password_again or new_password == '':
            raise forms.ValidationError('两次密码不同，请重新输入')
        return self.cleaned_data

    # 验证旧密码是否正确
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password', '')
        if not self.user.check_password(old_password):
            raise forms.ValidationError('旧的密码错误')
        return old_password

class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(label='邮箱', required=True,
                             widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': '请输入绑定过的邮箱地址'}))
    verification_code = forms.CharField(label='验证码', required=False,
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '点击"发送验证码"发送到邮箱'}))
    new_password = forms.CharField(label='新密码',
                                   widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '请输入新密码'}))

    def __init__(self, *args, **kwargs):    # 传入request才能取到下面的session
        if 'request' in kwargs:
            self.request = kwargs.pop('request')
        super(ForgotPasswordForm, self).__init__(*args, **kwargs)

    def clean_email(self):    # 验证用户名是否存在
        email = self.cleaned_data['email'].strip()
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError('邮箱不存在')
        return email

    def clean_verification_code(self):
        # 验证码不能为空
        verification_code = self.cleaned_data.get('verification_code', '').strip()
        if verification_code == '':
            raise forms.ValidationError('验证码不能为空')

        # 验证码是否正确
        code = self.request.session.get('forgot_password_code', '')  # 忘记密码生成的验证码
        verification_code = self.cleaned_data.get('verification_code', '')  # 用户填写的验证码
        if not (code != '' and code == verification_code):
            raise forms.ValidationError('验证码错误')
        return verification_code