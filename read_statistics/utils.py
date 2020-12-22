import datetime
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from .models import ReadNum, ReadDetail

def read_statistics_once_read(request, obj):
    ct = ContentType.objects.get_for_model(obj)
    key = "%s_%s_read" % (ct.model, obj.pk)

    if not request.COOKIES.get(key):
        # 阅读总数+1
        """
        获取逻辑的处理逻辑，可以使用get_or_create()替换
        if ReadNum.objects.filter(content_type=ct, object_id=obj.pk).count():  # 存在记录
            readnum = ReadNum.objects.get(content_type=ct, object_id=obj.pk)  # 获得阅读数
        else:
            readnum = ReadNum(content_type=ct, object_id=obj.pk)  # 创建阅读记录
        """
        readnum, created = ReadNum.objects.get_or_create(content_type=ct, object_id=obj.pk)
        readnum.read_num += 1  # 计数加一
        readnum.save()

        # 当天阅读数+1
        date = timezone.now().date()    # 获取当前日期
        """
        if ReadDetail.objects.filter(content_type=ct, object_id=obj.pk, date=date).count():    # 如果存在记录，直接获取
            readDetail = ReadDetail.objects.get(content_type=ct, object_id=obj.pk, date=date)
        else:    # 不存在记录，先创建记录
            readDetail = ReadDetail(content_type=ct, object_id=obj.pk, date=date)
        """
        readDetail, created = ReadDetail.objects.get_or_create(content_type=ct, object_id=obj.pk, date=date)
        readDetail.read_num += 1
        readDetail.save()
    return key

def get_seven_days_read_data(content_type):
    today = timezone.now().date()
    dates = []
    read_nums = []
    for i in range(7, 0, -1):
        date = today - datetime.timedelta(days=i)    # 获取前七天阅读数
        dates.append(date.strftime('%m/%d'))    # html需要字符串，所以返回的date，需要用strftime格式化为字符串

        read_details = ReadDetail.objects.filter(content_type=content_type, date=date)
        result = read_details.aggregate(read_num_sum=Sum('read_num'))    # 对同一天的read_num字段求和
        read_nums.append(result['read_num_sum'] or 0)
    return dates, read_nums

def get_today_hot_data(content_type):
    today = timezone.now().date()
    read_details = ReadDetail.objects.filter(content_type=content_type, date=today).order_by('-read_num')    # 先筛选，然后按照read_num字段由大到小排序
    return read_details[:7]    # 取前七条

def get_yesterday_hot_data(content_type):
    yesterday = timezone.now().date() - datetime.timedelta(days=1)
    read_details = ReadDetail.objects.filter(content_type=content_type, date=yesterday).order_by('-read_num')    # 先筛选，然后按照read_num字段由大到小排序
    return read_details[:7]