from django.shortcuts import get_object_or_404,render
from django.http import Http404
from django.shortcuts import render_to_response
from django.template import loader
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required,user_passes_test
from .models import Users
from django.contrib import auth
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone
from datetime import  datetime,timedelta
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.settings import api_settings
import JSON
import requests
from .models import *

class GetWordsView(APIView):
    '''
    背单词接口
    '''
    def post(self, request):
        id = request.data.get('user_id')
        user = User.objects.get(user_id = id)
        new_words_num = user.setting_new_word
        review_words_num = user.setting_review_word
        JSON = {}
        JSON['method'] = "words_TodayTask"
        data = {}
        history = user.study_history.split(',')
        already = self.count(history)
        data['date'] = len(history) + 1
        word_list = self.getwords(user.bitmap, new_words_num, review_words_num, already)
        data['word_List'] = word_list
        JSON['data'] = data

        return Response(JSON)


    def count(self, history):
        count = 0
        for hi in history:
            count += int(hi.split(':')[-1])
        return count

    def getwords(self, bitmap, new, old, already):
        wordlist = []
        words = Word.objects.all()
        if old < already:
            old = already
        for i, wd in enumerate(words[0:already]):
            if int(bitmap[i]) < 3:
                word = {}
                pos = wd.pos
                sentence = wd.sentence[0:pos] + '(' + wd.sentence[pos] + ')' + wd.sentence[pos+1:]
                word["word_Sentence"] = sentence
                word["word_PartOfSpeech"] = wd.part_of_speech
                word["word_Sense"] = wd.meaning
                word["word_RemberedTimes"] = int(bitmap[i])
                similar = ""
                for w in words:
                    if w.word == wd.word:
                        po = w.pos
                        similar = w.sentence[0:po] + '(' + w.sentence[po] + ')' + w.sentence[po+1:]
                        break
                word["word_SimilarSentence"] = similar
                wordlist.append(word)
                old -= 1
            if old == 0:
                break
        for i, wd in enumerate(words[already:]):
            word = {}
            pos = wd.pos
            sentence = wd.sentence[0:pos] + '(' + wd.sentence[pos] + ')' + wd.sentence[pos+1:]
            word["word_Sentence"] = sentence
            word["word_PartOfSpeech"] = wd.part_of_speech
            word["word_Sense"] = wd.meaning
            word["word_RemberedTimes"] = int(bitmap[i])
            similar = ""
            for w in words:
                if w.word == wd.word:
                    po = w.pos
                    similar = w.sentence[0:po] + '(' + w.sentence[po] + ')' + w.sentence[po+1:]
                    break
            word["word_SimilarSentence"] = similar
            wordlist.append(word)
            new -= 1
            if new == 0:
                break
        return wordlist






appid = "wxc1de7ec30d311389"
appsecret = "03eef9f0991167b49014792091e4f091"

class LoginView(APIView):
    """
    微信登录逻辑
    """

    def post(self, request):
        # 前端发送code到后端,后端发送网络请求到微信服务器换取openid
        code = request.data.get('code')
        if not code:
            return Response({'message': '缺少code'}, status=status.HTTP_400_BAD_REQUEST)

        url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code" \
            .format(appid, appsecret, code)
        r = requests.get(url)
        res = json.loads(r.text)
        openid = res['openid'] if 'openid' in res else None
        # session_key = res['session_key'] if 'session_key' in res else HTTP_414_REQUEST_URI_TOO_LONGNone
        if not openid:
            return Response({'message': '微信调用失败'}, status=status.HTTP_503)

        # 判断用户是否第一次登录
        try:
            user = Users.objects.get(user_name=openid)
        except Exception:
            # 微信用户第一次登陆,新建用户
            # username = request.data.get('nickname')
            # sex = request.data.get('sex')
            # avatar = request.data.get('avatar')
            user = Users.objects.create(user_name=openid)
            # user.set_password(openid)

        # 手动签发jwt
        # jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        # jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

        # payload = jwt_payload_handler(user)
        # token = jwt_encode_handler(payload)

        resp_data = {
                "userid":user.id,
        }

        return Response(resp_data)

    def get(self, request):
        respdata={
                "userid":"hello",
                }
        return Response(respdata)

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

        


