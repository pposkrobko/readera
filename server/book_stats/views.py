from django.views.generic import ListView, TemplateView
from book_stats.models import BookStats, BookStatsHistory, Book
from django.db.models import Sum, Count, Avg, Max, Min
from django.shortcuts import render


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


class HistoryView(TemplateView):
    template_name = "book_stats/history.html"

    def get_context_data(self, **kwargs):
        context = super(HistoryView, self).get_context_data(**kwargs)
        books = BookStats.objects.filter(user=self.request.user, state__in=(BookStats.DONE, BookStats.FORSAKEN))
        books_data = []
        for b in books:
            print("TITLE: "+b.book.title)
            temp = {}
            temp['title'] = b.book.title
            temp['author'] = b.book.author.name
            temp['pages'] = b.book.max_pages
            temp['start'] = BookStatsHistory.objects.filter(book_stats=b).aggregate(Min('time'))['time__min']
            temp['end'] = BookStatsHistory.objects.filter(book_stats=b).aggregate(Max('time'))['time__max']
            temp['days'] = (temp['end'] - temp['start']).days
            temp['onpage'] = b.on_page
            temp['done'] = b.state == BookStats.DONE
            temp['speed'] = round(temp['onpage'] / temp['days'], 2)

            books_data.append(temp)

        context['books'] = books_data
        return context

# Create your views here.
def get_new_book_form(request):
    if request.method == 'POST':
        form = AddNewBookForm(request.POST)
        if form.is_valid():
            new_book = form.save()
            # commit=False tells Django that "Don't send this to database yet.
            # I have more things I want to do with it."

            stats = BookStats()
            stats.book = new_book
            stats.user = request.user
            stats.save()

            return HttpResponseRedirect("/stats/user/")
    else:
        form = AddNewBookForm()
    return render(request, 'book_stats/new-book-form.html', {"example_form": form})