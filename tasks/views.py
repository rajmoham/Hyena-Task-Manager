from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView
from django.urls import reverse
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm , TeamForm, TeamInviteForm, TaskForm, TeamEdit
from tasks.helpers import login_prohibited
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden
from tasks.models import Team, Invitation, Notification, Task

from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render

def custom_404(request, exception):
    """Display error page"""
    return render(request, '404.html', status = 404)

@login_required
def dashboard(request):
    """Display the current user's dashboard."""
    current_user = request.user
    form = TeamForm()
    user_teams = Team.objects.filter(author=current_user)
    user_notifications = Notification.objects.filter(user=current_user)
    return render(request, 'dashboard.html', {'user': current_user, "user_teams" : user_teams, "user_notifications": user_notifications})

#TODO: Turn this into a form view class
@login_required
def create_team(request):
    if request.method == 'POST':
        if request.user.is_authenticated:
            current_user = request.user
            form = TeamForm(request.POST)
            if form.is_valid():
                titleCleaned = form.cleaned_data.get("title")
                descriptionCleaned = form.cleaned_data.get('description')
                team = Team.objects.create(author=current_user, title = titleCleaned, description=descriptionCleaned)
                team.members.add(current_user) # adds only the team creator for now
                notification = Notification.objects.create(
                    user=current_user,
                    title="New Team Created: " + titleCleaned,
                    description="You have created a new team",
                    actionable=False
                )
                return redirect('dashboard')
            else:
                return render(request, 'create_team.html', {'form': form})
        else:
            return redirect('log_in')
    else:
        if request.user.is_authenticated:
            form = TeamForm()
            return render(request, 'create_team.html', {'form': form})
        else:
            return redirect('log_in')
    

@login_prohibited
def home(request):
    """Display the application's start/home screen."""

    return render(request, 'home.html')

@login_required
def show_team(request, team_id):
    """Show the team details: team name, description, members"""
    try:
        team = Team.objects.get(id=team_id)
        tasks = Task.objects.filter(author=team)
    except ObjectDoesNotExist:
        return redirect('dashboard')
    else:
        return render(request, 'show_team.html', {'team': team, 'tasks': tasks})

#TODO: Turn this into a form view class
@login_required  
def create_task(request, team_id):
    """Allow the user to create a Task for their Team"""
    if request.method == "POST":
        if request.user.is_authenticated:
            current_team = Team.objects.get(id = team_id)
            form = TaskForm(request.POST)
            if form.is_valid():
                titleCleaned = form.cleaned_data.get("title")
                descriptionCleaned = form.cleaned_data.get('description')
                dueDateCleaned = form.cleaned_data.get("due_date")
                task = Task.objects.create(author=current_team, title = titleCleaned, description=descriptionCleaned, due_date=dueDateCleaned)

                return redirect('show_team', team_id)
            else:
                return render(request, 'create_task.html', {'team': current_team,'form': form})
        else:
            return redirect('log_in')
    else:
        if request.user.is_authenticated:
            form = TaskForm()
            current_team = Team.objects.get(id = team_id)
            return render(request, 'create_task.html', {'team': current_team,'form': form})
        else:
            return redirect('log_in')


@login_required
def invite(request, team_id):
    team = get_object_or_404(Team, pk=team_id)

    if request.user != team.author:
        messages.error(request, "You do not have permission to invite members to this team.")
        return redirect('show_team', team_id=team_id)

    form = TeamInviteForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user_email = form.cleaned_data['email']
        invitation = Invitation.objects.create(
            team=team,
            email=user_email,
            status=Invitation.INVITED
        )
        messages.success(request, 'Invitation sent successfully.')

        return redirect('show_team', team_id=team_id)

    return render(request, 'invite.html', {'form': form, 'team': team})


@login_required
def list_invitations(request):
    invitations = Invitation.objects.filter(email=request.user.email)
    return render(request, 'list_invitations.html', {'invitations': invitations})

@login_required
def accept_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, id=invitation_id, email=request.user.email)
    invitation.team.members.add(request.user)
    invitation.status = Invitation.ACCEPTED
    invitation.save()
    messages.success(request, "You have joined the team!")
    return redirect('dashboard')

@login_required
def decline_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, pk=invitation_id, email=request.user.email)

    if invitation.status != Invitation.DECLINED:
        invitation.status = Invitation.DECLINED
        invitation.save()
        messages.success(request, "You have declined the invitation.")
    else:
        messages.info(request, "You have already declined this invitation.")

    return redirect('list_invitations')




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


class LogInView(LoginProhibitedMixin, View):
    """Display login screen and handle user login."""

    http_method_names = ['get', 'post']
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def get(self, request):
        """Display log in template."""

        self.next = request.GET.get('next') or ''
        return self.render()

    def post(self, request):
        """Handle log in attempt."""

        form = LogInForm(request.POST)
        self.next = request.POST.get('next') or settings.REDIRECT_URL_WHEN_LOGGED_IN
        user = form.get_user()
        if user is not None:
            login(request, user)
            return redirect(self.next)
        messages.add_message(request, messages.ERROR, "The credentials provided were invalid!")
        return self.render()

    def render(self):
        """Render log in template with blank log in form."""

        form = LogInForm()
        return render(self.request, 'log_in.html', {'form': form, 'next': self.next})


def log_out(request):
    """Log out the current user"""

    logout(request)
    return redirect('home')


class PasswordView(LoginRequiredMixin, FormView):
    """Display password change screen and handle password change requests."""

    template_name = 'password.html'
    form_class = PasswordForm

    def get_form_kwargs(self, **kwargs):
        """Pass the current user to the password change form."""

        kwargs = super().get_form_kwargs(**kwargs)
        kwargs.update({'user': self.request.user})
        return kwargs

    def form_valid(self, form):
        """Handle valid form by saving the new password."""

        form.save()
        login(self.request, self.request.user)
        return super().form_valid(form)

    def get_success_url(self):
        """Redirect the user after successful password change."""

        messages.add_message(self.request, messages.SUCCESS, "Password updated!")
        return reverse('dashboard')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    """Display user profile editing screen, and handle profile modifications."""

    model = UserForm
    template_name = "profile.html"
    form_class = UserForm

    def get_object(self):
        """Return the object (user) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Profile updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)


class SignUpView(LoginProhibitedMixin, FormView):
    """Display the sign up screen and handle sign ups."""

    form_class = SignUpForm
    template_name = "sign_up.html"
    redirect_when_logged_in_url = settings.REDIRECT_URL_WHEN_LOGGED_IN

    def form_valid(self, form):
        self.object = form.save()
        login(self.request, self.object)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

class TeamUpdateView(UpdateView):
    """Display team editing screen, and handle team details modifications."""

    model = TeamForm
    template_name = "edit_team.html"
    form_class = TeamForm

    def get_object(self):
        """Return the object (team) to be updated."""
        user = self.request.user
        return user

    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Team updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)
    


    


