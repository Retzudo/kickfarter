from app.forms import UserCreationForm, LoginForm
from django.contrib.auth import authenticate, logout, login
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect


def index(request):
    return render(request, 'app/index.html')


def signup(request):
    if request.user.is_authenticated():
        return redirect(reverse('index'))
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            user = authenticate(email=request.POST['email'], password=request.POST['password1'])
            login(request, user)
            return render(request, 'app/signup_success.html')
    else:
        form = UserCreationForm()

    return render(request, 'app/signup.html', context={'form': form})


def login_view(request):
    if request.user.is_authenticated():
        return redirect(reverse('profile'))

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(email=form.cleaned_data['email'], password=form.cleaned_data['password'])
            if user:
                login(request, user)
                return redirect(reverse('index'))
    else:
        form = LoginForm()

    return render(request, 'app/login.html', context={'form': form})


def logout_view(request):
    logout(request)
    return redirect(reverse('index'))


def profile(request):
    return render(request, 'app/profile.html')