from django.conf.urls import url
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from book_stats import views

urlpatterns = [
    url(r'^user/$', login_required(views.ProfileView.as_view()), name="profile"),
    url(r'^user/bookstats/', views.BookStatsHistoryAdd.as_view()),
    url(r'^stat/', login_required(views.ChartsView.as_view()), name="stats"),
    url(r'^history/', login_required(views.HistoryView.as_view()), name="history"),
    url(r'^favourite/', login_required(views.FavouriteView.as_view()), name="favourite"),
    url(r'^get_new_book_form/$', views.get_new_book_form, name="form"),
    url(r'^forsake/$', views.forsake, name="forsake"),
    url(r'^love/$', views.love, name="love"),
    url(r'^books-stats/$', views.BooksStatsView.as_view(), name="books-stats"),
    url(r'^authors-stats/$', views.AuthorsStatsView.as_view(), name="authors-stats"),


]