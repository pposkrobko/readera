from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from book_stats import views

urlpatterns = [
    url(r'^user/', login_required(views.ProfileView.as_view()), name ="profile"),
    url(r'^stat/', login_required(TemplateView.as_view(template_name="book_stats/stats.html")), name = "stats"),
]