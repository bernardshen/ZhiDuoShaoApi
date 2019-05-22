from django.conf.urls import include, url
from rest_framework import routers
from api import views


route = routers.DefaultRouter()
# route.register(r'login', views.LoginView)

urlpatterns = [
    url('api/', include(route.urls)),
    url('api/login', views.LoginView.as_view()),
    url('api/yiju/',views.YijuEveryday.as_view()),
    url('api/pushlike/',views.Pushlike.as_view()),
    url('api/findword/',views.Findword.as_view()),
]
