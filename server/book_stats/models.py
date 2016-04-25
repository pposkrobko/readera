from django.db import models
from django.contrib.auth.models import User
import datetime

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Author(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete = models.CASCADE)
    max_pages = models.IntegerField()


class BookStats(models.Model):
    book = models.ForeignKey(Book, on_delete = models.CASCADE)
    user = models.ForeignKey(User)
    on_page = models.IntegerField(default=0)
    reading_time = models.DurationField(default = datetime.timedelta(seconds = 1))
    last_time_used = models.DateField(auto_now=True)

    def __str__(self):
        return self.title


class BookStatsHistory(models.Model):
    book_stats = models.ForeignKey(BookStats, on_delete=models.CASCADE)
    time = models.DateField(auto_now=True)
    pages_read = models.IntegerField()


# Create your models here.
