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
from datetime import  datetime,timedelta,date
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.settings import api_settings
import json
import requests
from .models import *
from datetime import datetime
import json
from django.db.models import Sum, Count

date_map = {
    0: '〇',
    1: '一',
    2: '二',
    3: '三',
    4: '四',
    5: '五',
    6: '六',
    7: '七',
    8: '八',
    9: '九'
}
  
def chinese2digits(num, type):
    str_num = str(num)
    result = ''
    if type == 0:
        for i in str_num:
            result = '{}{}'.format(result, date_map.get(int(i)))
    if type == 1:
        result = '{}十{}'.format(date_map.get(int(str_num[0])), date_map.get(int(str_num[1])))
    if type == 2:
        result = '十{}'.format(date_map.get(int(str_num[1])))
    if type == 3:
        result = '十'
    if type == 4:
        result = '二十'
    return result

def ch_date(date_year,date_month,date_day):
    year=chinese2digits(date_year,0)
    if date_month == 10:
        month = chinese2digits(date_month, 3)
    if date_month > 10:
        month = chinese2digits(date_month, 2)
    if date_month < 10:
        month = chinese2digits(date_month, 0)
    if date_day < 10:
        day = chinese2digits(date_day, 0)
    if 10 < date_day < 20:
        day = chinese2digits(date_day, 2)
    if date_day > 20:
        day = chinese2digits(date_day, 1)
    if date_day == 10:
        day = chinese2digits(date_day, 3)
    if date_day == 20:
        day = chinese2digits(date_day, 4)
    return year,month,day


ERROR_CODE = {
    'success':           0, 
    'userid_invalid':    1,
    'message_invalid':   2,
    'pushid_invalid':    3,
    'word_not_found':    4,
    'data_invalid':      5,
    'server_no_response':6, 
}


def GenError(code, is_error=True):
    msg = {
        'error': is_error,
        'code':  code,
    }
    return msg


class FinishTask(APIView):
    '''
    背完今日单词
    '''
    def post(self, request):
        try:
            id = int(request.date.get['userID'])
            data = request.data.get('data')
        except:
            return Response(GenError(ERROR_CODE['message_invalid']), status=status.HTTP_400_BAD_REQUEST)
        
        # id = int(request.GET['userID'])
        try:
            user = Users.objects.get(id=id)
        except:
            return Response(GenError(ERROR_CODE['userid_invalid']))
        
        # data = request.GET['data']
        wordlist = json.loads(data)['data']['word_List']
        oldcount = 0
        newcount = 0
        bitmap = list(user.bitmap)
        for word in wordlist:
            word_id = word['word_id']
            orig = word['word_RemberedTimes']
            change = word['word_RemberedTimesChange']

            if orig == 0:
                newcount += 1
                if change == -1:
                    times = 1
                else:
                    times = 2
            else:
                times = orig + change
                oldcount += 1

            bitmap[word_id] = str(times)

        user.bitmap = bitmap
        today = str(oldcount) + ':' + str(newcount) + ','
        user.study_history += today
        user.save()

        return Response({'message':'恭喜完成背诵！'})

class StopAndSave(APIView):
    '''
    中途退出
    '''
    def post(self, request):
        try:
            id = int(request.data.get['userID'])
            data = request.data.get('save')
        except:
            return Response(GenError(ERROR_CODE['message_invalid']), status=status.HTTP_400_BAD_REQUEST)
        
        try:
            last = TempSave.objects.get(userID=id)
        except:
            last = None

        if last is None:
            last = TempSave.objects.create(userID=id, saved=data, date=timezone.now())
            last.save()
        else:
            last.saved = data
            last.date = timezone.now()
            last.save()

        return Response(data)

upper = 5
class GetWordsView(APIView):
    '''
    背单词接口s
    '''
    def post(self, request):
        print(str(request))
        try:
            id = int(request.data.get('userID'))
        except:
            return Response(GenError(ERROR_CODE['message_invalid']), status=status.HTTP_400_BAD_REQUEST)

        # id = int(request.GET['userID'])
        flag = self.FirstTimeToday(id)

        if flag == True:
            JSON = self.getword(id)
        else:
            JSON = self.getsaved(id)

        return Response(JSON)

    def FirstTimeToday(self, id):

        try:
            obj = TempSave.objects.get(userID=id)
        except:
            obj = None

        if obj is None:
            return True
        day = str(obj.date).split()[0]
        today = str(datetime.now()).split()[0]
        return day != today

    def getsaved(self, id):
        save = TempSave.objects.get(userID=id)
        content = eval(save.saved)
        return content

    def getword(self, id):
        user = Users.objects.get(id = id)
        new_words_num = user.setting_new_word
        review_words_num = user.setting_review_word
        JSON = {}
        JSON['method'] = "words_TodayTask"
        data = {}
        history = user.study_history.split(',')[0:-1]
        already = self.count(history)
        data['date'] = len(history) + 1
        word_list = self.getwords(user.bitmap, new_words_num, review_words_num, already)
        data['word_List'] = word_list
        JSON['data'] = data
        return JSON

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
            if int(bitmap[i]) < upper:
                word = {}
                pos = wd.pos
                sentence = wd.sentence[0:pos] + '(' + wd.sentence[pos] + ')' + wd.sentence[pos+1:]
                word["word_Sentence"] = sentence
                word["word_PartOfSpeech"] = wd.part_of_speech
                word["word_Sense"] = wd.meaning
                word["word_RemberedTimes"] = int(bitmap[i])
                word["word_RemberedTimesChange"] = 0
                word["word_Show"] = False
                word["word_id"] = wd.id
                similar = ""
                for w in words:
                    if w.word == wd.word and w.id != wd.id:
                        po = w.pos
                        similar = w.sentence[0:po] + '(' + w.sentence[po] + ')' + w.sentence[po+1:]
                        break
                word["word_SimilarSentence"] = similar
                wordlist.append(word)
                old -= 1
            if old == 0:
                break
        for wd in words[already:]:
            word = {}
            pos = wd.pos
            sentence = wd.sentence[0:pos] + '(' + wd.sentence[pos] + ')' + wd.sentence[pos+1:]
            word["word_Sentence"] = sentence
            word["word_PartOfSpeech"] = wd.part_of_speech
            word["word_Sense"] = wd.meaning
            word["word_RemberedTimes"] = 0
            word["word_RemberedTimesChange"] = 0
            word["word_Show"] = False
            word["word_id"] = wd.id
            similar = ""
            for w in words:
                if w.word == wd.word and w.id != wd.id:
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
        try:
            code = request.data.get('code')
        except:
            return Response(ERROR_CODE['message_invalid'], status=status.HTTP_400_BAD_REQUEST)

        url = "https://api.weixin.qq.com/sns/jscode2session?appid={0}&secret={1}&js_code={2}&grant_type=authorization_code" \
            .format(appid, appsecret, code)
        r = requests.get(url)
        res = json.loads(r.text)
        openid = res['openid'] if 'openid' in res else None

        if not openid:
            return Response(GenError(ERROR_CODE['server_no_response']), status=status.HTTP_503_SERVICE_UNAVAILABLE)

        # 判断用户是否第一次登录
        try:
            user = Users.objects.get(user_name=openid)
        except Exception:
            user = Users.objects.create(user_name=openid)

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
        try:
            user_id=int(request.GET['userID'])
            date_get=request.GET['date']
            date_Y,date_M,date_D=map(int,date_get.split('-'))
            date_request=date(date_Y,date_M,date_D)
            num=int(request.GET['num'])
        except:
            # return HttpResponse('error')
            return Response(ERROR_CODE['invalid_message'], status=status.HTTP_400_BAD_REQUEST)
        
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
        if len(collect)==0:
            collect=[-1]
        else:
            collect=list(map(int,collect.split(',')))
        #获取每日一句信息
        try:
            yijus=Yiju.objects.filter(date__lte=date_request).order_by('-date')[:num]
        except:
            resp_data = {
                "message": "yiju error",
                "date":date_request,
            }
            return Response(resp_data)

        yiju_list=[]
        for yiju in yijus:
            data={
                "push_id":      yiju.id,
                "date":         ch_date(date_year=yiju.date.year,date_month=yiju.date.month,date_day=yiju.date.day),
                "dynasty":      yiju.dynasty,
                "author":       yiju.author,
                "title":        yiju.title,
                "article":      yiju.article,
                "content":      yiju.content,
                "like_count":   yiju.like,
                "like":         int(yiju.id in collect)
            }
            yiju_list.append(data)
        
        resp_data={
            "swiper_List":  yiju_list
        }

        return Response(resp_data)

class Pushlike_yiju(APIView):
    def get(self, request):
        try:
            user_id=int(request.GET['userID'])
            push_id=int(request.GET['pushID'])
            like=int(request.GET['like'])
        except:
            return Response(GenError(ERROR_CODE['message_invalid']), status=status.HTTP_400_BAD_REQUEST)

        #获取用户及推送信息
        try:
            user=Users.objects.get(id=user_id)
        except:
            return Response(GenError(ERROR_CODE['userid_invalid']))
        
        try:
            push = Yiju.objects.get(id=push_id)
        except:
            return Response(GenError(ERROR_CODE['pushid_invalid']))

        collect=user.yiju_collected
        if len(collect) == 0:
            collect = []
        else:
            collect = list(map(int,collect.split(',')))
        #return Response(collect)

        if like == 1:
            if push_id not in collect:
                collect.append(push_id)
                collect = list(map(str,collect))
                collect = ','.join(collect)
                user.yiju_collected = collect
                user.save()
                push.like = push.like+1
                push.save()
        else:
            if push_id in collect:
                collect.remove(push_id)
                collect = list(map(str,collect))
                collect = ','.join(collect)
                user.yiju_collected = collect
                user.save()
                push.like = push.like-1
                push.save()

        return Response(push.like)


class Pushlike_dict(APIView):
    def get(self, request):
        try:
            user_id = int(request.GET['userID'])
            dict_id = int(request.GET['dictID'])
            like = int(request.GET['like'])
        except:
            return Response(GenError(ERROR_CODE['message_invalid']), status=status.HTTP_400_BAD_REQUEST)

        #获取用户及推送信息
        try:
            user = Users.objects.get(id=user_id)
        except:
            return Response(GenError(ERROR_CODE['userid_invalid']))

        collect = user.dictionary_collected
        if len(collect) == 0:
            collect=[]
        else:
            collect = list(map(int,collect.split(',')))
        #return Response(collect)

        if like == 1:
            if dict_id not in collect:
                collect.append(dict_id)
                collect = list(map(str,collect))
                collect = ','.join(collect)
                user.dictionary_collected = collect
                user.save()
        else:
            if dict_id in collect:
                collect.remove(dict_id)
                collect = list(map(str,collect))
                collect = ','.join(collect)
                user.dictionary_collected = collect
                user.save()

        return Response('success')

        
class Findword(APIView):
    def get(self, request):
        
        try:
            word_request = request.GET['word']
        except:
            return Response(GenError(ERROR_CODE['message_invalid']), status=status.HTTP_400_BAD_REQUEST)
        
        word_list = Dictionary.objects.filter(word=word_request)
        if word_list is None:
            return Response(GenError(ERROR_CODE['word_not_found']))
        
        data=[]
        for w in word_list:
            if len(w.meaning)<=1:
                continue
                
            word_dict={
                "id":w.id,  #该词的一种意义的id，用于收藏
                "sense":w.meaning, #该词的这种意义是什么
                "sentence":w.sentence.split('#'),   #例句，是个list
                "pronunciation":w.pronunciation, #该词这种意义的词性
                "source":w.source.split('#'),
            }
            data.append(word_dict)
        
        return Response(data)

class InitDict(APIView):
    def get(self,request):
        try:
            password=request.GET['password']
        except:
            return Response('error')

        if password!='Ruanjian2019':
            return Response('error')

        Dictionary.objects.all().delete()

        file=open(r'/home/ubuntu/zdsapi/ZDSApi/api/static/api/dictionary.txt',encoding='utf-8')
        #file=open(r'api\dictionary.txt',encoding="utf-8")
        lines=file.readlines()
        for line in lines:
            line=line.split(' ')
            add=Dictionary(word=line[0],pronunciation=line[1],meaning=line[2],sentence=line[3],source=line[4])
            add.save()
        
        return Response('init success')


# 学习设置
class SetLearning(APIView):
    def post(self, request):
        try:
            user_id = request.data.get('user_id')
            word_num = int(request.data.get('word_num'))
            review_num = int(request.data.get('review_num'))
            mode = int(request.data.get('mode'))
        except:
            Response(GenError(ERROR_CODE['message_invalid']), status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = Users.objects.get(id=user_id)
        except:
            return Response(GenError(ERROR_CODE['userid_invalid']))

        user.mode = mode
        user.setting_new_word = word_num
        user.setting_review_word = review_num
        user.save()

        return Response(GenError(ERROR_CODE['success'], False))



# 返回收藏
class ReturnCollect(APIView):
    def post(self, request):
        try:
            user_id = int(request.data.get('user_id'))
        except:
            return Response(GenError(ERROR_CODE['message_invalid']), status=status.HTTP_400_BAD_REQUEST)

        try:
            user = Users.objects.get(id=user_id)
        except:
            return Response(GenError(ERROR_CODE['userid_invalid']))
        
        dict_c = user.dictionary_collected
        yiju_c = user.yiju_collected
        word_c = user.word_collected
        
        dict_c = [int(n) for n in dict_c.split(',')]
        yiju_c = [int(n) for n in yiju_c.split(',')]
        word_c = [int(n) for n in word_c.split(',')]

        dict_l = [{'id': Dictionary.objects.get(w).id, 'name': Dictionary.objects.get(w).word} for w in dict_c]
        yiju_l = [{'id': Yiju.objects.get(w).id, 'name': Yiju.objects.get(w).title} for w in yiju_c]
        word_l = [{'id': Word.objects.get(w).id, 'name': Word.objects.get(w).word} for w in word_c]

        resdata = {
            'yiju': yiju_l,
            'vocab': dict_c,
            'learn': word_c,
        }

        Response(resdata)


class ReturnProcess(APIView):
    def post(self, request):
        try:
            user_id = int(request.data.get('user_id'))
        except:
            return Response(GenError(ERROR_CODE['message_invalid']), status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(id=user_id)
        except:
            return Response(GenError(ERROR_CODE['userid_invalid']))

        total_num = Word.objects.all().count()
        hist = [int(n.split(':')[1]) for n in user.study_history]
        
        s = 0
        for n in hist:
            s += n
        progress = s/total_num

        book = Book.objects.get(id=user.book_id)

        resdata = {
            'name': book.name,
            'progress': progress,
            'numbers': hist,
        }

        return Response(resdata)

