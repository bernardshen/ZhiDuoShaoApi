from django.conf.urls import include, url
from rest_framework import routers
from api import views


route = routers.DefaultRouter()
# route.register(r'login', views.LoginView)

urlpatterns = [
    url('api/', include(route.urls)),
    url('api/login', views.LoginView.as_view()),
]
