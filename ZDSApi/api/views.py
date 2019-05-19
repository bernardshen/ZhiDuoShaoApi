from django.shortcuts import get_object_or_404,render
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Users,Authors,Books,Publishers,Loan,Comment
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from datetime import  datetime,timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request
from rest_framework.settings import APISettings
import json

class WechatLoginView(APIView):
    """
    微信登录逻辑
    """

    def post(self, request):
        # 前端发送code到后端,后端发送网络请求到微信服务器换取openid
        code = request.data.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

        url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code" \
            .format(settings.APP_ID, settings.APP_KEY, code)
        r = request.get(url)
        res = json.loads(r.text)
        openid = res['openid'] if 'openid' in res else None
        # session_key = res['session_key'] if 'session_key' in res else None
        if not openid:
            return Response({'message': '微信调用失败'}, status=status.HTTP_503)

        # 判断用户是否第一次登录
        try:
            user = User.objects.get(openid=openid)
        except Exception:
            # 微信用户第一次登陆,新建用户
            username = request.data.get('nickname')
            sex = request.data.get('sex')
            avatar = request.data.get('avatar')
            user = User.objects.create(username=username, sex=sex, avatar=avatar)
            user.set_password(openid)

        # 手动签发jwt
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)

        resp_data = {
            "user_id": user.id,
            "username": user.username,
            "avatar": user.avatar,
            "token": token,
        }

        return Response(resp_data)

class YijuEveryday(APIView):
    #处理每日一句的请求
    def get(self, request):
        #收到/yiju/userID=xxx&date=xxxx-xx-xx$num=x
        user_id=request.GET('userID')
        date=request.GET('date')
        num=request.GET('num')
        
        #获取用户信息
        try:
            userinfo=Users.objects.get(id=user_id)
        except:
            resp_data = {
                "message": "user_id error"
            }
            return Response(resp_data)
        
        #获取收藏——字符串形式
        collect=userinfo.yiju_collected
        #获取收藏——列表形式
        collect=list(map(int,collect.split(',')))

        #获取每日一句信息
        try:
            yijus=Yiju.objects.filter(date__lte=date).order_by('-date')[:num]
        except:
            resp_data = {
                "message": "yiju error"
            }
            return Response(resp_data)

        yiju_list=[]
        for yiju in yijus:
            data={
                "push_id":      yiju.id,
                "date":         yiju.date,
                "dynasty":      yiju.dynasty,
                "author":       yiju.author,
                "title":        yiju.title,
                "article":      yiju.article,
                "content":      yiju.content,
                "like_count":   yiju.like,
                "like":         yiju.id in collect
            }
            yiju_list.append(data)
        
        resp_data={
            "swiper_List":  yiju_list
        }

        return Response(resp_data)

        







