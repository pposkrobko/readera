from rest_framework import serializers
from book_stats.models import BookStats, Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('title', 'author', 'max_pages')


class BooksStatsSerializer(serializers.ModelSerializer):
    book = BookSerializer(read_only=True)

    class Meta:
        model = BookStats
        fields = ('state', 'on_page', 'reading_time', 'book')

