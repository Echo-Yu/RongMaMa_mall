import random
from django.http import HttpResponse
from django_redis import get_redis_connection
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from RongMa_mall.libs.captcha.captcha import captcha
from users.models import User
from verifications import constants
from verifications.serializers import ImageCodeCheckSerializer
from celery_tasks.sms.tasks import send_sms_code


class ImageCodeView(APIView):
    """图片验证码"""
    def get(self, request, image_code_id):
        """
        获取图片验证码
        """
        # 生成验证码图片
        text, image = captcha.generate_captcha()
        redis_conn = get_redis_connection("verify_codes")
        redis_conn.setex("img_%s" % image_code_id, constants.IMAGE_CODE_REDIS_EXPIRES, text)
        # 固定返回验证码图片数据，不需要REST framework框架的Response帮助我们决定返回响应数据的格式
        # 所以此处直接使用Django原生的HttpResponse即可
        return HttpResponse(image, content_type="images/jpg")

# GET /sms_codes/(?P<mobile>1[3-9]\d{9})/?image_code_id=xxx&text=xxx
# url('^sms_codes/(?P<mobile>1[3-9]\d{9})/$', views.SMSCodeView.as_view()),
class SMSCodeView(GenericAPIView):
    """短信验证码 传入参数： mobile, image_code_id, text"""
    """
    检查图片验证码
    检查是否在60s内有发送记录
    生成短信验证码
    保存短信验证码与发送记录
    发送短信
    """
    serializer_class = ImageCodeCheckSerializer

    def get(self, request, mobile):
        """
        创建短信验证码
        """
        # 判断图片验证码, 判断是否在60s内
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        # 生成短信验证码
        sms_code = '%06d' % random.randint(0,999999)
        # 保存短信验证码与发送记录
        redis_conn = get_redis_connection('verify_codes')
        pl = redis_conn.pipeline()
        pl.setex('sms_%s' % mobile, constants.SMS_CODE_REDIS_EXPIRES,sms_code)
        pl.setex('send_flag_%s' % mobile,constants.SEND_CODE_REDIS_EXPIRES, 1)
        pl.execute()

        # 发送短信验证码
        # sms_code_expires = str(constants.IMAGE_CODE_REDIS_EXPIRES // 60)
        # ccp = CCP()
        # ccp.send_template_sms(mobile,[sms_code, sms_code_expires],constants.SMS_CODE_TEMP_ID)
        # return Response({'message':'ok'})
        expires = str(constants.IMAGE_CODE_REDIS_EXPIRES // 60)
        send_sms_code.delay(mobile,sms_code,expires,constants.SMS_CODE_TEMP_ID)
        return Response({'message':'ok'})

# url(r'^usernames/(?P<username>\w{5,20})/count/$', views.UsernameCountView.as_view()),
class UsernameCountView(APIView):
    """ 用户名数量"""
    def get(self,request,username):
        count = User.objects.filter(username=username).count()
        data={
            'username':username,
            'count':count
        }
        return Response(data)

# GET mobiles/(?P<mobile>1[3-9]\d{9})/count
# url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$', views.MobileCountView.as_view()),
class MobileCountView(APIView):
    """手机号数量"""
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        data= {
            'mobile':mobile,
            'count':count
        }
        return Response(data)

