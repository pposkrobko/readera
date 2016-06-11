from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    url(r'^user/', login_required(TemplateView.as_view(template_name="book_stats/user.html")), name ="profile"),
    url(r'^stat/', login_required(TemplateView.as_view(template_name="book_stats/stats.html")), name = "stats"),
]