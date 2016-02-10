from app.forms import UserCreationForm, LoginForm, ProjectForm
from app.models import Project
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect


def index(request):
    projects = Project.objects.filter(status=0)
    return render(request, 'app/index.html', context={'projects': projects})


def discover(request):
    projects = Project.objects.filter(status=0)
    return render(request, 'app/discover.html', context={'projects': projects})


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


@login_required
def start_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.instance.created_by = request.user
            form.save()
            # return redirect(reverse('view_project', id=project.id))
    else:
        form = ProjectForm()

    return render(request, 'app/start_project.html', context={'form': form})
