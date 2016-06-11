from django.views.generic import ListView, TemplateView
from book_stats.models import BookStats, BookStatsHistory
from django.db.models import Sum, Count, Avg, Max

class ProfileView(ListView):
    template_name = "book_stats/user.html"

    def get_queryset(self):
        return BookStats.objects.filter(user=self.request.user).filter(state=BookStats.IN_PROGRESS)


class ChartsView(TemplateView):
    template_name = "book_stats/stats.html"

    def get_context_data(self, **kwargs):
        context = super(ChartsView, self).get_context_data(**kwargs)
        books = BookStats.objects.filter(user=self.request.user)
        history = BookStatsHistory.objects.filter(book_stats__user=self.request.user).values('time').annotate(Sum('pages_read'))
        context.update({
            'books' : books,
            'stats' : books.values('book__author__name').annotate(Sum('on_page')),
            'history' : history.order_by('time')
        })
        context.update(books.aggregate(Sum('on_page'), Count('book'), Avg('book__max_pages'), Count('book__author')))
        context.update(history.aggregate(Max('pages_read__sum')))
        return context

# Create your views here.
