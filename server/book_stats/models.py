from django.db import models
from django.contrib.auth.models import User
import datetime

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Author(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete = models.CASCADE)
    max_pages = models.IntegerField()

    def __str__(self):
        return "".join((str(self.author), ": ", str(self.title)))


class BookStats(models.Model):

    DONE = "Książka już przeczytana."
    IN_PROGRESS = "W trakcie czytania."
    FORSAKEN = "Zrezygnowano z czytania."

    book_states = (
        (DONE, DONE),
        (IN_PROGRESS, IN_PROGRESS),
        (FORSAKEN, FORSAKEN)
    )

    state = models.CharField(choices = book_states, max_length=30, default=IN_PROGRESS)
    book = models.ForeignKey(Book, on_delete = models.CASCADE)
    user = models.ForeignKey(User)
    on_page = models.IntegerField(default=0)
    reading_time = models.DurationField(default = datetime.timedelta(seconds = 1))
    last_time_used = models.DateField(auto_now=True)
    loves = models.BooleanField(default=False)

    def __str__(self):
        return "".join((str(self.user), ": ", str(self.book)))


class BookStatsHistory(models.Model):
    book_stats = models.ForeignKey(BookStats, on_delete=models.CASCADE)
    time = models.DateField(auto_now=True)
    pages_read = models.IntegerField()

