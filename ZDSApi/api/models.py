from django.db import models
import datetime
from django.utils import timezone
from django.contrib.auth.models import User

class TempSave(models.Model):
    userID = models.IntegerField()
    saved = models.TextField()
    date = models.DateTimeField()

class Users(models.Model):
    user_name = models.CharField(max_length=50)
    bitmap = models.CharField(max_length=1005, default=1000*'0')
    word_collected = models.TextField(default="")
    dictionary_collected = models.TextField(default="")
    yiju_collected = models.TextField(default="")
    setting_new_word = models.IntegerField(default=10)
    setting_review_word = models.IntegerField(default=10)
    study_history = models.TextField(default="")
    mode = models.IntegerField(default=0) #0表示积累模式
    book_name = models.IntegerField(defalut=None)
    def __str__(self):
        return self.user_name

class Word(models.Model):
    word = models.CharField(max_length=20)
    pos = models.IntegerField()
    meaning = models.TextField()
    sentence = models.TextField()
    article = models.TextField()
    book_id = models.IntegerField()
    part_of_speech = models.TextField() #词性
    def __str__(self):
        return self.word

class Dictionary(models.Model):
    word = models.CharField(max_length=20)
    pronunciation = models.TextField()#发音
    meaning = models.TextField()
    sentence = models.TextField()
    source = models.TextField()
    def __str__(self):
        return self.word

class Book(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name

class Yiju(models.Model):
    date = models.DateField()
    title = models.TextField()
    dynasty = models.TextField()
    author = models.TextField()
    article = models.TextField()
    content = models.TextField()
    like = models.IntegerField(default=0)
    def __self__(self):
        return self.title



