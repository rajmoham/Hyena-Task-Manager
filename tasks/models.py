from django.core.validators import RegexValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.db import models
from libgravatar import Gravatar
from django.utils import timezone

class User(AbstractUser):
    """Model used for user authentication, and team members related information."""

    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[RegexValidator(
            regex=r'^@\w{3,}$',
            message='Username must consist of @ followed by at least three alphanumericals'
        )]
    )
    first_name = models.CharField(max_length=50, blank=False)
    last_name = models.CharField(max_length=50, blank=False)
    email = models.EmailField(unique=True, blank=False)
    total_tasks_completed = models.IntegerField(default=0, blank=False)


    class Meta:
        """Model options."""

        ordering = ['last_name', 'first_name']

    def full_name(self):
        """Return a string containing the user's full name."""

        return f'{self.first_name} {self.last_name}'

    def gravatar(self, size=120):
        """Return a URL to the user's gravatar."""

        gravatar_object = Gravatar(self.email)
        gravatar_url = gravatar_object.get_image(size=size, default='mp')
        return gravatar_url

    def mini_gravatar(self):
        """Return a URL to a miniature version of the user's gravatar."""

        return self.gravatar(size=60)

"""Teams Created by users"""
class Team(models.Model):

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length =  50, blank=False)
    description = models.CharField(max_length=280, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(User, related_name='teams')
    class Meta:
        """Model options."""

        ordering = ['-created_at']


class Invitation(models.Model):
    INVITED = 'invited'
    ACCEPTED = 'accepted'
    DECLINED = 'declined'

    Choice_status = (
        (INVITED, 'Invited'),
        (ACCEPTED, 'Accepted'),
        (DECLINED, 'Declined'),
    )

    team = models.ForeignKey(Team, related_name = 'invitations', on_delete=models.CASCADE)
    email = models.EmailField()
    status = models.CharField(max_length = 20, choices = Choice_status, default = INVITED)
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__ (self):
        return self.email

"""Notification created for certain actions"""
class Notification(models.Model):
    title = models.CharField(max_length=50, blank=False)
    description = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    actionable = models.BooleanField()
    invitation = models.ForeignKey(Invitation, on_delete=models.SET_NULL, null=True, blank=True)
    seen = models.BooleanField(default=False)

    class Meta:
        """Model options."""

        ordering = ['-created_at']

    def mark_as_seen(self):
        self.seen = True

"""Task Created by a Team"""
class Task(models.Model):

    author = models.ForeignKey(Team, on_delete=models.CASCADE)
    title = models.CharField(max_length =  50, blank=False)
    description = models.CharField(max_length=280, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(
        blank=False,
        validators=[MinValueValidator(
            limit_value=timezone.now()
            )]
    )
    assigned_members = models.ManyToManyField(User, related_name='tasks')
    is_complete = models.BooleanField(blank=False, default=False)
    is_archived = models.BooleanField(blank=False, default=False)
    points = models.IntegerField(default=1, blank=False)

    def toggle_task_status(self):
        if self.is_complete:
            self._mark_task_incomplete()
        else:
            self._mark_task_complete()

    def _mark_task_complete(self):
        self.is_complete = True

    def _mark_task_incomplete(self):
        self.is_complete = False

    def toggle_archive(self):
        if self.is_archived:
            self._unarchive_task()
        else:
            self._archive_task()

    def _archive_task(self):
        self.is_archived = True

    def _unarchive_task(self):
        self.is_archived = False

    

    


    class Meta:
        """Model Options"""

        ordering = ['due_date']


""" One User can have many Teams and One Team can have many Users: Many to Many
    One Team can have Many Tasks but One Task can only have one Team: One to Many
    One User can have Many Tasks and One Tasks can have many Users: Many to Many"""
