from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
# GET / image_codes / (?P < image_code_id > [\w -]+) /
from django_redis import get_redis_connection
from rest_framework.views import APIView

from RongMa_mall.libs.captcha.captcha import captcha
from verifications import constants


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
from django.shortcuts import render

# Create your views here.
