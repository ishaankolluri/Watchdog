from django.conf.urls import url

from . import views

app_name = "simulator"
urlpatterns = [
    url(r'^', views.LoginView.as_view(), name='login'),
]