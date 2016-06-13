from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import ListView, TemplateView
from rest_framework.response import Response
from book_stats.forms import AddNewBookForm
from book_stats.models import BookStats, BookStatsHistory, Book, Author
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
        books = BookStats.objects.filter(user=self.request.user).exclude(state=BookStats.IN_PROGRESS)
        books_data = []
        for b in books:
            temp = {}
            temp['title'] = b.book.title
            temp['author'] = b.book.author.name
            temp['pages'] = b.book.max_pages
            temp['start'] = BookStatsHistory.objects.filter(book_stats=b).aggregate(Min('time'))['time__min']
            temp['end'] = BookStatsHistory.objects.filter(book_stats=b).aggregate(Max('time'))['time__max']
            temp['days'] = (temp['end'] - temp['start'] + datetime.timedelta(days=1)).days
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


class BooksStatsView(TemplateView):
    template_name = "book_stats/books-stats.html"

    def get_context_data(self, **kwargs):
        context = super(BooksStatsView, self).get_context_data(**kwargs)
        count = BookStats.objects.values('book').annotate(readers=Count('book')).order_by('readers')[:100]
        pop = []
        for c in count:
            pop.append([c['readers'], Book.objects.get(pk=c['book'])])
        context['popular'] = pop

        context['fast'] = get_fastest_books(Book.objects.all())[:100]

        return context


class AuthorsStatsView(TemplateView):
    template_name = "book_stats/authors-stats.html"

    def get_context_data(self, **kwargs):
        context = super(AuthorsStatsView, self).get_context_data(**kwargs)
        count = BookStats.objects.values('book__author').annotate(readers=Count('book__author')).order_by('readers')[:100]
        print(count)
        pop = []
        for c in count:
            pop.append([c['readers'], Author.objects.get(pk=c['book__author'])])
        context['popular'] = pop

        context['fast'] = get_fastest_authors(Author.objects.all())[:100]


        return context

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


def love(request):
    if request.method == 'POST':
        book = Book.objects.get(title=request.POST['title'], author__name=request.POST['author'])
        book_stat = BookStats.objects.get(user=request.user, book=book)
        book_stat.loves = not book_stat.loves
        book_stat.save()
        return HttpResponseRedirect(request.POST['return'])


def restore(request):
    if request.method == 'POST':
        book = Book.objects.get(title=request.POST['title'], author__name=request.POST['author'])
        book_stat = BookStats.objects.get(user=request.user, book=book)
        book_stat.state = BookStats.IN_PROGRESS
        book_stat.save()
        return HttpResponseRedirect("/stats/user/")


def progress(request):
    if request.method == 'POST':
        book = Book.objects.get(title=request.POST['title'], author__name=request.POST['author'])
        book_stat = BookStats.objects.get(user=request.user, book=book)
        pages_read = int(request.POST['page'])
        if pages_read == book_stat.on_page:
            return HttpResponseRedirect("/stats/user/")

        BookStatsHistory.objects.create(book_stats=book_stat, pages_read=pages_read-book_stat.on_page)
        book_stat.on_page += pages_read-book_stat.on_page
        if book_stat.on_page >= book.max_pages:
            book_stat.state = BookStats.DONE
            book_stat.save()
            return HttpResponseRedirect("/stats/history/")
        book_stat.save()
        return HttpResponseRedirect("/stats/user/")

def get_fastest_books(books):
    result = []
    for b in books:
        done = BookStats.objects.filter(book=b, state=BookStats.DONE)
        if len(done) == 0:
            continue
        speed = 0
        for d in done:
            entr = BookStatsHistory.objects.filter(book_stats=d)
            days = (entr.aggregate(Max('time'))['time__max'] - entr.aggregate(Min('time'))['time__min'] +
                    datetime.timedelta(days=1)).days
            speed += b.max_pages / days
        result.append([round(speed / len(done), 2), len(done), b])

    result.sort()
    return result

def get_fastest_authors(authors):
    result = []
    for a in authors:
        books = get_fastest_books(Book.objects.filter(author=a))
        if len(books) == 0:
            continue
        result.append([round(sum(x for x, *_ in books) / len(books), 2), len(books), a])

    result.sort()
    return result
