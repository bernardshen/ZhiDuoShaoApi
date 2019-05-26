from django.contrib import admin
from .models import Users, Word, Dictionary, Book, Yiju, TempSave

admin.site.register(Users)
admin.site.register(Word)
admin.site.register(Dictionary)
admin.site.register(Book)
admin.site.register(Yiju)
admin.site.register(TempSave)

# Register your models here.
