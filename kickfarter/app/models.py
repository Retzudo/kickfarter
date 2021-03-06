import datetime

from app.exceptions import BackingException
from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import MinValueValidator
from django.db import models


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

    def pledge(self, amount, project, reward_tier=None):
        if project.created_by == self:
            raise BackingException('You can\'t back your own projects')
        if project in self.pledged_to.all():
            raise BackingException('You have already backed this project')
        if project.status != Project.STATUS_ACTIVE:
            raise BackingException('You can only back active projects')

        pledge = Pledge(project=project, user=self, amount=amount, chosen_reward_tier=reward_tier)
        pledge.save()
        return pledge

    def __str__(self):
        return self.name if self.name else self.email


class Project(models.Model):
    STATUS_ACTIVE = 0
    STATUS_SUCCESSFUL = 1
    STATUS_NOT_FUNDED = 2
    STATUS_CANCELED = 3
    STATUS_DRAFT = 4

    CURRENCY_USD = 0
    CURRENCY_EUR = 1
    CURRENCY_CAD = 2

    PROJECT_STATUS = [
        (STATUS_ACTIVE, 'ACTIVE'),
        (STATUS_SUCCESSFUL, 'SUCCESSFUL'),
        (STATUS_NOT_FUNDED, 'NOT_FUNDED'),
        (STATUS_CANCELED, 'CANCELED'),
        (STATUS_DRAFT, 'DRAFT'),
    ]

    CURRENCIES = [
        (CURRENCY_USD, '$'),
        (CURRENCY_EUR, '€'),
        (CURRENCY_CAD, 'CAD'),
    ]

    DEFAULT_DURATION = 60  # in days

    title = models.CharField(max_length=255)
    description = models.TextField()
    goal = models.FloatField(validators=[MinValueValidator(1)])
    cover_image = models.ImageField(null=True, blank=True)
    published_on = models.DateTimeField(null=True, blank=True)
    status = models.IntegerField(choices=PROJECT_STATUS, default=STATUS_DRAFT)
    currency = models.IntegerField(choices=CURRENCIES, default=CURRENCY_USD)
    created_by = models.ForeignKey('User', related_name='projects_created', on_delete=models.CASCADE)
    pledges = models.ManyToManyField('User', through='Pledge', related_name='pledged_to')

    @classmethod
    def from_db(cls, db, field_names, values):
        """
        Every time a project object is loaded from database, update its status.
        This is an expensive way of doing the status updates but considering
        this is a hobby project it shouldn't matter too much. I just wanted to avoid cron jobs and
        other convoluted asynchronous systems.
        """
        instance = super().from_db(db, field_names, values)
        instance.update_status()
        return instance

    @property
    def total_pledged_amount(self):
        return sum([pledge.amount for pledge in self.pledge_set.all()])

    @property
    def percentage_funded(self):
        return (self.total_pledged_amount / self.goal) * 100

    @property
    def is_draft(self):
        return self.status == Project.STATUS_DRAFT

    @property
    def finished_on(self):
        return self.published_on + datetime.timedelta(days=self.DEFAULT_DURATION)

    def publish(self):
        self.status = Project.STATUS_ACTIVE
        self.published_on = datetime.datetime.now(datetime.timezone.utc)

    def cancel(self):
        self.status = Project.STATUS_CANCELED

    def timedelta_remaining(self, relative_to=None):
        """
        :param relative_to: datetime.datetime
        :return: datetime.timedelta
        """
        if not relative_to:
            relative_to = datetime.datetime.now(datetime.timezone.utc)

        return self.finished_on - relative_to

    def update_status(self):
        # If the project is active and there's no time remaining
        if self.status == self.STATUS_ACTIVE and self.timedelta_remaining().total_seconds() <= 0:
            if self.total_pledged_amount >= self.goal:
                self.status = self.STATUS_SUCCESSFUL
            else:
                self.status = self.STATUS_NOT_FUNDED

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
