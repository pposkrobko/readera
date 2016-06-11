from book_stats.models import BookStatsHistory
from rest_framework import serializers

class BookStatsHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookStatsHistory
        exclude = ('time','book_stats')