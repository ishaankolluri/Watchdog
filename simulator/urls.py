from django.conf.urls import url

from . import views

app_name = "simulator"

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/$', views.login_req, name='login'),
    url(r'^loggedin/$', views.loggedin, name='loggedin'),
    url(r'^logout/$', views.logout_req, name='logout'),
    url(r'^signup/', views.signup, name='signup'),
    url(r'^signedup/', views.signedup, name='signedup'),
    url(r'^profile/', views.profile, name='profile'),
    url(r'^getstockdata_views/', views.getstockdata_views,
        name='getstockdata_views'),
    url(r'^market_execution/', views.market_execution,
        name="market_execution"),
]
