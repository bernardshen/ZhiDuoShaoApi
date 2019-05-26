from django.conf.urls import include, url
from rest_framework import routers
from api import views
from django.conf import settings
from django.conf.urls.static import static

route = routers.DefaultRouter()
# route.register(r'login', views.LoginView)

urlpatterns = [
    url('api/', include(route.urls)),
    url('api/login', views.LoginView.as_view()),
    url('api/yiju/',views.YijuEveryday.as_view()),
    url('api/pushlike/',views.Pushlike.as_view()),
    url('api/findword/',views.Findword.as_view()),
    url('api/initdict/',views.InitDict.as_view()),
    url('api/getwords/', views.GetWordsView.as_view()),
    url('api/save/', views.StopAndSave.as_view()),
    url('api/finish', views.FinishTask.as_view()),
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)