from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from app.exceptions import BackingException


PROJECT_STATUS = [
    (0, 'ACTIVE'),
    (1, 'SUCCESSFUL'),
    (2, 'NOT_FUNDED'),
    (3, 'CANCELED'),
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
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    """Basic user because we don't want Django's."""
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    objects = UserManager()

    USERNAME_FIELD = 'email'

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return self.name

    def pledge(self, amount, project, reward=None):
        if project.creator == self:
            raise BackingException('You can\'t back your own projects')
        if project.status != 0:
            raise BackingException('You can only back active projects')
        if project in self.pledged_to.all():
            raise BackingException('You have already backed this project')

        pledge = Pledge(project=project, user=self, amount=amount, reward=reward)
        pledge.save()
        return pledge


class Project(models.Model):
    description = models.TextField()
    goal = models.FloatField()
    pledges = models.ManyToManyField('User', through='Pledge', related_name='pledged_to')
    created_by = models.ForeignKey('User', related_name='projects_created', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_created=True)
    status = models.IntegerField(choices=PROJECT_STATUS, default=PROJECT_STATUS[0])
    cover_image = models.ImageField()


class Pledge(models.Model):
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    user = models.ForeignKey('User', related_name='pledges', on_delete=models.CASCADE)
    amount = models.FloatField()
    chosen_reward = models.ForeignKey('Reward', related_name='pledges', on_delete=models.CASCADE, null=True, blank=True)


class Reward(models.Model):
    project = models.ForeignKey('Project', related_name='reward_tiers', on_delete=models.CASCADE)
    description = models.TextField()
    minimum_amount = models.FloatField()


class Comment(models.Model):
    project = models.ForeignKey('Project', related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey('User', related_name='comments')
    text = models.TextField()


class Update(models.Model):
    project = models.ForeignKey('Project', related_name='updates', on_delete=models.CASCADE)
    text = models.TextField()
