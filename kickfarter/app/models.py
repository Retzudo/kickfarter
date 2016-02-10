from app.exceptions import BackingException
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinValueValidator
from django.db import models

PROJECT_STATUS = [
    (0, 'ACTIVE'),
    (1, 'SUCCESSFUL'),
    (2, 'NOT_FUNDED'),
    (3, 'CANCELED'),
    (4, 'DRAFT'),
]


class UserManager(BaseUserManager):
    """Boilerplate code because Django..."""
    def create_user(self, email, password, name=None):
        user = self.model(email=self.normalize_email(email), name=name)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, name=None):
        user = self.model(email=self.normalize_email(email), name=name)
        user.set_password(password)
        user.is_admin = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Basic user because we don't want Django's user class."""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    objects = UserManager()

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return self.name

    @property
    def is_staff(self):
        return self.is_admin

    def pledge(self, amount, project, reward=None):
        if project.created_by == self:
            raise BackingException('You can\'t back your own projects')
        if project.status != 0:
            raise BackingException('You can only back active projects')
        if project in self.pledged_to.all():
            raise BackingException('You have already backed this project')

        pledge = Pledge(project=project, user=self, amount=amount, chosen_reward_tier=reward)
        pledge.save()
        return pledge

    def __str__(self):
        return self.name if self.name else self.email


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    goal = models.FloatField(validators=[MinValueValidator(1)])
    cover_image = models.ImageField(null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    status = models.IntegerField(choices=PROJECT_STATUS, default=4)
    created_by = models.ForeignKey('User', related_name='projects_created', on_delete=models.CASCADE)
    pledges = models.ManyToManyField('User', through='Pledge', related_name='pledged_to')

    @property
    def total_pledged_amount(self):
        return sum([pledge.amount for pledge in self.pledge_set.all()])

    @property
    def percentage_funded(self):
        return (self.total_pledged_amount / self.goal) * 100

    def publish(self):
        self.status = 0

    def __str__(self):
        return self.title


class Pledge(models.Model):
    amount = models.FloatField()
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    user = models.ForeignKey('User', related_name='pledges', on_delete=models.CASCADE)
    chosen_reward_tier = models.ForeignKey('RewardTier', related_name='pledges', on_delete=models.CASCADE, null=True, blank=True)


class RewardTier(models.Model):
    description = models.TextField()
    minimum_amount = models.FloatField()
    project = models.ForeignKey('Project', related_name='reward_tiers', on_delete=models.CASCADE)


class Comment(models.Model):
    text = models.TextField()
    project = models.ForeignKey('Project', related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey('User', related_name='comments')  # Don't delete comments on user deletion


class Update(models.Model):
    text = models.TextField()
    project = models.ForeignKey('Project', related_name='updates', on_delete=models.CASCADE)
    backers_only = models.BooleanField(default=False)
