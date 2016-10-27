from django.conf.urls import url

from . import views

app_name = "simulator"
urlpatterns = [
 #   url(r'^', views.LoginView.as_view(), name='login'),
    url(r'^login$', views.login, name='login'),
 	url(r'^$', views.home, name='home'),
 	url(r'^signup/', views.signup, name='signup'),
 	url(r'^signedup/', views.signedup, name='signedup'),
]