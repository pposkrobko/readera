"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.generic import TemplateView
from django.contrib.auth.views import login, logout
from server import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^register$', views.registerRedirect, name='register-redirect'),
    url(r'^login$', views.loginRedirect, name='login-redirect'),
    url(r'^logout$', views.logoutRedirect, name='logout-redirect'),
    url(r'^stats/', include('book_stats.urls')),
    url(r'^admin/', admin.site.urls),
    #url(r'^accounts/login/$', login, {'template_name': 'admin/login.html'},
    #    name='login'),
    #url(r'^accounts/logout/$', logout, {'next_page': '/'}, name='logout'),
]
