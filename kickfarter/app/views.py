from django.shortcuts import render


def index(request):
    return render(request, 'app/index.html')


def signup(request):
    return render(request, 'app/signup.html')


def login(request):
    return render(request, 'app/login.html')
