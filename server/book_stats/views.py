from django.views.generic import ListView, TemplateView
from book_stats.models import BookStats, BookStatsHistory
from django.db.models import Sum, Count, Avg

class ProfileView(ListView):
    template_name = "book_stats/user.html"

    def get_queryset(self):
        return BookStats.objects.filter(user=self.request.user).filter(state=BookStats.IN_PROGRESS)


class ChartsView(TemplateView):
    template_name = "book_stats/stats.html"

    def get_context_data(self, **kwargs):
        context = super(ChartsView, self).get_context_data(**kwargs)
        books = BookStats.objects.filter(user=self.request.user)
        context.update({
            'books' : books,
            'stats' : books.values('book__author__name').annotate(Sum('on_page'))
        })
        context.update(books.aggregate(Sum('on_page'), Count('book'), Avg('book__max_pages')))
        return context

# Create your views here.
