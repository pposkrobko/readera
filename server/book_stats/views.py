from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from rest_framework.response import Response
from book_stats.forms import AddNewBookForm
from book_stats.models import BookStats, BookStatsHistory, Book
from django.db.models import Sum, Count, Avg, Max, Min
from rest_framework import generics, permissions, status
from book_stats.serializers import BookStatsHistorySerializer
import datetime
from django.shortcuts import render


class ProfileView(ListView):
    template_name = "book_stats/user.html"

    def get_queryset(self):
        return BookStats.objects.filter(user=self.request.user).filter(state=BookStats.IN_PROGRESS).order_by("-last_time_used", "-pk")


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



class BookStatsHistoryAdd(generics.CreateAPIView):
    queryset = BookStatsHistory.objects.all()
    serializer_class = BookStatsHistorySerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request):
        request.data.update({})
        serializer = self.get_serializer(data=request.data)
        statistics = BookStats.objects.get(book__title=request.data['book'], user=request.user)
        serializer.is_valid(raise_exception=True)
        serializer.validated_data['book_stats'] = statistics
        statistics.on_page = statistics.on_page + int(request.data['pages_read'])
        statistics.reading_time = statistics.reading_time + datetime.timedelta(minutes=int(request.data['minutes']))
        if statistics.on_page > statistics.book.max_pages:
            statistics.on_page = statistics.book.max_pages
            statistics.state = BookStats.DONE
        statistics.save()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class FavouriteView(ListView):
    template_name = "book_stats/favourite.html"

    def get_queryset(self):
        return BookStats.objects.filter(user=self.request.user, loves=True).order_by("-last_time_used")


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
    else:
        form = AddNewBookForm()
    return render(request, 'book_stats/new-book-form.html', {"example_form": form})


def forsake(request):
    if request.method == 'POST':
        book = Book.objects.get(title=request.POST['title'], author__name=request.POST['author'])
        book_stat = BookStats.objects.get(user=request.user, book=book)
        book_stat.state = BookStats.FORSAKEN
        book_stat.save()
        return HttpResponseRedirect("/stats/user/")

    print("A TERRIBLE ERROR")


def love(request):
    if request.method == 'POST':
        book = Book.objects.get(title=request.POST['title'], author__name=request.POST['author'])
        book_stat = BookStats.objects.get(user=request.user, book=book)
        book_stat.loves = not book_stat.loves
        book_stat.save()
        return HttpResponseRedirect(request.POST['return'])

    print("A TERRIBLE ERROR")
