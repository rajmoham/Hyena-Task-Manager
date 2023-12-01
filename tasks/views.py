from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm , TeamForm, TeamInviteForm, TaskForm, TeamEdit
from tasks.helpers import login_prohibited, calculate_task_complete_score
from django.core.exceptions import ObjectDoesNotExist
from django.http import HttpResponseForbidden, HttpResponse
from django.db.models import Q
from tasks.models import Team, Invitation, Notification, Task, User
from django.template import loader
from django.shortcuts import render
from django.http import Http404
from django.utils import timezone

def custom_404(request, exception):
    """Display error page"""
    return render(request, '404.html', status = 404)

@login_required
def dashboard(request):
    """Display the current user's dashboard."""
    current_user = request.user 
    form = TeamForm()
    user_teams = Team.objects.filter(Q(author=current_user) | Q(members=current_user)).distinct()
    user_notifications = Notification.objects.filter(user=current_user)

    #All Tasks Assigned to the user
    user_tasks = Task.objects.filter(assigned_members=current_user)

    late_tasks = Task.objects.filter(assigned_members=current_user, due_date__lt=timezone.now())
    

    return render(request, 'dashboard.html', {'user': current_user,
                                                "user_teams" : user_teams,
                                                "user_notifications": user_notifications,
                                                'user_tasks': user_tasks,
                                                'late_tasks':late_tasks})

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
        # team = Team.objects.get(id=team_id)
        # tasks = Task.objects.filter(author=team)
        members, current_team, tasks = calculate_task_complete_score(team_id)
        # members = set()
        # for task in tasks:
        #     members.update(task.assigned_members.all())

    except ObjectDoesNotExist:
        return redirect('dashboard')
    except Http404:
        return redirect('dashboard')
    else:
        return render(request, 'show_team.html', {'team': current_team, 'tasks': tasks, 'members': members})

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
        return redirect('log_in')
    
@login_required
def edit_task(request, task_id):
    current_task = Task.objects.get(id=task_id)
    current_team = current_task.author
    if request.method == 'POST':
        form = TaskForm(instance=current_task, data=request.POST)
        if form.is_valid():
            messages.success(request, "Task updated!")
            form.save()
            return redirect('show_team', current_team.id)
    else:
        form = TaskForm(instance=current_task)
    return render(request, 'edit_task.html', {'task': current_task, 'form': form})
    
@login_required
def delete_task(request, task_id):
    current_user = request.user
    current_task = Task.objects.get(id=task_id)
    current_team = current_task.author
    if current_task.author == current_team:
        if current_team.author == current_user:
            current_task.delete()
            messages.add_message(request, messages.SUCCESS, "Task deleted!")
        else:
            messages.add_message(request, messages.ERROR, "You cannot delete a Task in a Team you did not create")
    else:
        messages.add_message(request, messages.ERROR, "You cannot delete another Teams Task")
    return redirect('show_team', current_team.id)

@login_required
def toggle_task_status(request, task_id):
    current_user = request.user
    try:
        task_to_toggle = Task.objects.get(id=task_id)
        current_team = task_to_toggle.author
        if (task_to_toggle.author == current_team) and (current_team.members.filter(id=current_user.id).exists()):
            task_to_toggle.toggle_task_status()
            task_to_toggle.save()
            messages.add_message(request, messages.SUCCESS, "Task status changed!")
        else: 
            messages.add_message(request, messages.ERROR, "You cannot change task status because you are not in this team")
            return redirect('dashboard')
    except ObjectDoesNotExist:
        return redirect('dashboard')
    else:
        return redirect('leaderboard', current_team.id)

@login_required
def toggle_task_archive(request, task_id):
    current_user = request.user
    try:
        task_to_toggle = Task.objects.get(id=task_id)
        current_team = task_to_toggle.author
        if (task_to_toggle.author == current_team) and (current_team.members.filter(id=current_user.id).exists()):
            task_to_toggle.toggle_archive()
            task_to_toggle.save()
            if task_to_toggle.is_archived :
                messages.add_message(request, messages.SUCCESS, "Task archived!")
            else:
                messages.add_message(request, messages.SUCCESS, "Task unarchived!")
        else: 
            messages.add_message(request, messages.ERROR, "You cannot toggle archive because you are not in this team")
            return redirect('dashboard')
    except ObjectDoesNotExist:
        return redirect('dashboard')
    else:
        return redirect('show_team', current_team.id)

@login_required
def leaderboard_view(request, team_id):
    try:
        members, current_team, tasks = calculate_task_complete_score(team_id)
        return render(request, 'show_team.html', {'members': members, 'team': current_team, 'tasks': tasks})

    except ObjectDoesNotExist:
        return redirect('dashboard')
    else:
        return redirect('show_team', team.id)

@login_required
def assign_member_to_task(request, task_id, user_id):
    current_task = Task.objects.get(id=task_id)
    current_team = current_task.author
    selected_user = User.objects.get(id = user_id)
    if selected_user in current_team.members.all():
        if selected_user in current_task.assigned_members.all():
            current_task.assigned_members.remove(selected_user)
        else:
            current_task.assigned_members.add(selected_user)
    return redirect('show_team', current_team.id)

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

    model = Team
    template_name = "edit_team.html"
    form_class = TeamForm

    def get_object(self):
        """Return the object (team) to be updated."""
        team_id = self.kwargs['team_id']
        team = Team.objects.get(id=team_id)
        return team
    
    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Team updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

def team_delete(request, pk):
    team = get_object_or_404(Team, pk=pk)  # Get your current team

    if request.method == 'POST':         # If method is POST,
        team.delete()                     # delete the team.
        return redirect('/')             # Finally, redirect to the homepage.

    return render(request, 'show_team.html', {'team': team})
    # If method is not POST, render the default template.
    
@login_required
def notifications(request):
    """Display Notifications associated with the user"""
    if request.user.is_authenticated:
        Notification.objects.create(
            user=request.user,
            title="Visited Notification Page",
            description="",
            actionable=False,
        )
        user_notifications = Notification.objects.filter(user=request.user)
        return render(request, 'notifications.html', {'user_notifications' : user_notifications})
    else:
        return redirect('log_in')
