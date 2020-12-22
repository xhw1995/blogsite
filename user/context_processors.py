from .forms import LoginForm

def login_modal_form(request):
    # 返回一个字典，键：login_modal_form，值：LoginForm的实例化
    return {'login_modal_form': LoginForm()}