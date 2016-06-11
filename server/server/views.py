from django.http import HttpResponsePermanentRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render


def index(request):
    if request.user.is_authenticated():
        return render(request, 'user.html')
    else:
        return render(request, 'index.html')

# Create your views here.
def loginRedirect(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            # Redirect to a success page.
        else:
            # Return a 'disabled account' error message
            ...
    else:
        # Return an 'invalid login' error message.
        ...
    return HttpResponsePermanentRedirect("/")


def registerRedirect(request):
    username = request.POST['username']
    email = request.POST['email']
    password = request.POST['password']
    User.objects.create_user(username, email, password)
    return HttpResponsePermanentRedirect("/")

def logoutRedirect(request):
    logout(request)
    return HttpResponsePermanentRedirect("/")