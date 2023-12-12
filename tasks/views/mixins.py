from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist
from tasks.models import Team, Task
from django.conf import settings
from django.http import Http404
from django.urls import reverse
from django.core.exceptions import ImproperlyConfigured
from django.contrib import messages

class TeamMemberProhibitedMixin:
    """Mixin that redirects when a user is not a team member."""

    redirect_if_not_team_member = None

    def dispatch(self, *args, **kwargs):
        """Redirect when not team member, or dispatch as normal otherwise."""
        team_id = kwargs.get('team_id', None)
        task_id = kwargs.get('task_id', None)

        if team_id != None:
            try:
                current_team = Team.objects.get(id=team_id)
            except ObjectDoesNotExist:
                raise Http404("Team does not exist")

            if not self.user_is_team_member(current_team):
                return self.handle_not_team_member(*args, **kwargs)

        if task_id != None:
            try: 
                current_task = Task.objects.get(id=task_id)
                current_team = Team.objects.get(id=current_task.author.id)
            except ObjectDoesNotExist:
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

            if not self.user_is_team_member(current_team):
                return self.handle_not_team_member(*args, **kwargs)

        return super().dispatch(*args, **kwargs)

    def handle_not_team_member(self, *args, **kwargs):
        url = self.get_redirect_when_not_team_member()
        return redirect(url)

    def user_is_team_member(self, team):
        return self.request.user.is_authenticated and (self.request.user in team.members.all() or self.request.user == team.author)

    def get_redirect_when_not_team_member(self):
        """Returns the url to redirect to when user is not team member."""
        if self.redirect_if_not_team_member is None:
            raise ImproperlyConfigured(
                "TeamMemberProhibitedMixin requires either a value for "
                "'redirect_if_not_team_member', or an implementation for "
                "'get_redirect_when_not_team_member()'."
            )
        else:
            return reverse(self.redirect_if_not_team_member)
        
class TeamAuthorProhibitedMixin:
    """Mixin that redirects when a user is not a team creator or author."""

    redirect_if_not_team_author = None

    def dispatch(self, *args, **kwargs):
        """Redirect when not team creator or author, or dispatch as normal otherwise."""
        team_id = kwargs.get('team_id', None)
        task_id = kwargs.get('task_id', None)

        if team_id is not None:
            try:
                current_team = Team.objects.get(id=team_id)
            except ObjectDoesNotExist:
                raise Http404("Team does not exist")

            if not self.user_is_team_author(current_team):
                return self.handle_not_team_author(*args, **kwargs)

        if task_id != None:
            try: 
                current_task = Task.objects.get(id=task_id)
                current_team = Team.objects.get(id=current_task.author.id)
            except ObjectDoesNotExist:
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

            if not self.user_is_team_author(current_team):
                return self.handle_not_team_author(*args, **kwargs)

        return super().dispatch(*args, **kwargs)

    def handle_not_team_author(self, *args, **kwargs):
        url = self.get_redirect_when_not_team_author()
        messages.add_message(self.request, messages.ERROR, "You cannot perform this task because you are not creator of the team")
        return redirect(url)

    def user_is_team_author(self, team):
        return self.request.user.is_authenticated and self.request.user == team.author and self.request.user in team.members.all()

    def get_redirect_when_not_team_author(self):
        """Returns the url to redirect to when user is not team author."""
        if self.redirect_if_not_team_author is None:
            raise ImproperlyConfigured(
                "TeamAuthorProhibitedMixin requires either a value for "
                "'redirect_if_not_team_author', or an implementation for "
                "'get_redirect_when_not_team_author()'."
            )
        else:
            return reverse(self.redirect_if_not_team_author)
        
class LoginProhibitedMixin:
    """Mixin that redirects when a user is logged in."""

    redirect_when_logged_in_url = None

    def dispatch(self, *args, **kwargs):
        """Redirect when logged in, or dispatch as normal otherwise."""
        if self.request.user.is_authenticated:
            return self.handle_already_logged_in(*args, **kwargs)
        return super().dispatch(*args, **kwargs)

    def handle_already_logged_in(self, *args, **kwargs):
        url = self.get_redirect_when_logged_in_url()
        return redirect(url)

    def get_redirect_when_logged_in_url(self):
        """Returns the url to redirect to when not logged in."""
        if self.redirect_when_logged_in_url is None:
            raise ImproperlyConfigured(
                "LoginProhibitedMixin requires either a value for "
                "'redirect_when_logged_in_url', or an implementation for "
                "'get_redirect_when_logged_in_url()'."
            )
        else:
            return self.redirect_when_logged_in_url