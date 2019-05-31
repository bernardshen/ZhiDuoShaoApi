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
    url('api/pushlike_yiju/',views.Pushlike_yiju.as_view()),
    url('api/pushlike_dict/',views.Pushlike_dict.as_view()),
    url('api/findword/',views.Findword.as_view()),
    url('api/initdict/',views.InitDict.as_view()),
    url('api/getwords', views.GetWordsView.as_view()),
    url('api/save', views.StopAndSave.as_view()),
    url('api/finish', views.FinishTask.as_view()),
    url('api/setlearn', views.SetLearning.as_view()),
    url('api/returncollected/', views.ReturnCollect.as_view()),
    url('api/schedule', views.ReturnProcess.as_view()),
    url('api/getsettings', views.GetSettings.as_view()),
    url('api/getpush/',views.GetPush.as_view()),
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
