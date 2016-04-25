from django.db import models
from django.contrib.auth.models import User
import datetime

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)


class BookStats(models.Model):
    book = models.ForeignKey(Book, on_delete = models.CASCADE)
    user = models.ForeignKey(User)
    on_page = models.IntegerField(default=0)
    reading_time = models.DurationField(default = datetime.timedelta(seconds = 1))


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Author:
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


# Create your models here.
