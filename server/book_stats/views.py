from django.views.generic import ListView
from book_stats.models import BookStats


class ProfileView(ListView):
    template_name = "book_stats/user.html"

    def get_queryset(self):
        return BookStats.objects.filter(user=self.request.user).filter(state=BookStats.IN_PROGRESS)


# Create your views here.
