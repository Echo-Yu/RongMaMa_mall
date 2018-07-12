# url(r'^users/$', views.UserView.as_view()),
from rest_framework.generics import CreateAPIView

from users.serializers import CreateUserSerializer


class UserView(CreateAPIView):
    """
    用户注册
    传入参数：
        username, password, password2, sms_code, mobile, allow
    """
    # 接收参数
    # 校验参数
    # 保存用户数据
    # 序列化返回数据
    serializer_class = CreateUserSerializer
