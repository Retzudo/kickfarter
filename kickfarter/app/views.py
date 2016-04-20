from app.forms import UserCreationForm, LoginForm, ProjectForm
from app.models import Project, RewardTier
from django.contrib.auth import authenticate, logout, login
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.urlresolvers import reverse
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404


def index(request):
    projects = Project.objects.filter(status=Project.STATUS_ACTIVE)
    return render(request, 'app/index.html', context={'projects': projects})


def discover(request):
    projects = Project.objects.filter(status=Project.STATUS_ACTIVE)
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
            return render(request, 'app/user/signup_success.html')
    else:
        form = UserCreationForm()

    return render(request, 'app/user/signup.html', context={'form': form})


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

    return render(request, 'app/user/login.html', context={'form': form})


def logout_view(request):
    logout(request)
    return redirect(reverse('index'))


@login_required
def profile(request):
    projects_created = request.user.projects_created.all()
    pledges = request.user.pledges.all()
    return render(request, 'app/user/profile.html', context={
        'projects_created': projects_created,
        'pledges': pledges,
    })


def view_project(request, id):
    """ Show the project if
    1. it is not a draft
    2. it is a draft and the logged in user is the owner
    else 404
    """
    project = get_object_or_404(Project, pk=id)
    num_backers = len(project.pledges.all())

    if project.is_draft:
        if request.user.is_authenticated() and (request.user == project.created_by or request.user.is_superuser):
            return render(request, 'app/project/view.html', context={
                'project': project,
                'num_backers': num_backers,
                'reward_tiers': project.reward_tiers.all(),
            })
        else:
            raise PermissionDenied()
    else:
        return render(request, 'app/project/view.html', context={
            'project': project,
            'num_backers': num_backers,
            'reward_tiers': project.reward_tiers.all(),
        })


@login_required
def start_project(request):
    RewardTierFormSet = inlineformset_factory(Project, RewardTier, fields=('minimum_amount', 'description'), extra=1)
    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            form.instance.created_by = request.user
            project = form.save()
            reward_tier_formset = RewardTierFormSet(request.POST, request.FILES, instance=project)
            if reward_tier_formset.is_valid():
                reward_tier_formset.save()
                return redirect(reverse('view_project', args=[form.instance.id]))
    else:
        form = ProjectForm()
        reward_tier_formset = RewardTierFormSet()

    return render(request, 'app/project/start.html', context={'form': form, 'reward_tier_formset': reward_tier_formset})


@login_required
def edit_project(request, id):
    project = get_object_or_404(Project, pk=id)

    if request.user == project.created_by or request.user.is_superuser:
        RewardTierFormSet = inlineformset_factory(Project, RewardTier, fields=('minimum_amount', 'description'), extra=0)
        if request.method == 'POST':
            form = ProjectForm(request.POST, files=request.FILES, instance=project)
            reward_tier_formset = RewardTierFormSet(request.POST, instance=project)
            if form.is_valid() and reward_tier_formset.is_valid():
                publish = request.POST.get('publish', None)
                if project.status == Project.STATUS_DRAFT and publish == '1':
                    form.instance.publish()
                form.save()
                reward_tier_formset.save()
        else:
            form = ProjectForm(instance=project)
            reward_tier_formset = RewardTierFormSet(instance=project)

        return render(request, 'app/project/edit.html', context={'form': form, 'reward_tier_formset': reward_tier_formset})
    else:
        raise PermissionDenied()


def error(request):
    return render(request, 'app/error/404.html')
