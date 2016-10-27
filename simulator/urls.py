from django.conf.urls import url

from . import views

app_name = "simulator"
urlpatterns = [
    url(r'^login$', views.login, name='login'),
    url(r'^$', views.home, name='home'),
    url(r'^signup/', views.signup, name='signup'),
    url(r'^signedup/', views.signedup, name='signedup'),
    url(r'^home/', views.home, name="home"),
    url(r'^profile/', views.profile, name='profile'),
]
