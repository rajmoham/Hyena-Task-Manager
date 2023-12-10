from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.views.generic.edit import FormView, UpdateView, DeleteView, CreateView
from django.urls import reverse, reverse_lazy
from tasks.forms import LogInForm, PasswordForm, UserForm, SignUpForm , TeamForm, TeamInviteForm, TaskForm
from tasks.helpers import login_prohibited, calculate_task_complete_score, team_member_prohibited_to_view_team, team_member_prohibited_to_customise_task
from django.http import HttpResponseForbidden, HttpResponse
from django.db.models import Q
from tasks.models import Team, Invitation, Notification, Task, User
from django.template import loader
from django.shortcuts import render
from django.http import Http404
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

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
    late_task_text = ", ".join([task.title for task in late_tasks[:10]])
    if (len(late_tasks) > 10):
        late_task_text += f" and {len(late_tasks) - 10} more."
    

    return render(request, 'dashboard.html', {'user': current_user,
                                                "user_teams" : user_teams,
                                                "user_notifications": user_notifications,
                                                'user_tasks': user_tasks,
                                                'late_tasks':late_tasks,
                                                'late_task_text':late_task_text})

# @login_required
# def create_team(request):
#     if request.method == 'POST':
#         current_user = request.user
#         form = TeamForm(request.POST)
#         if form.is_valid():
#             titleCleaned = form.cleaned_data.get("title")
#             descriptionCleaned = form.cleaned_data.get('description')
#             team = Team.objects.create(author=current_user, title = titleCleaned, description=descriptionCleaned)
#             team.members.add(current_user)
#             notification = Notification.objects.create(
#                 user=current_user,
#                 title="New Team Created: " + titleCleaned,
#                 description="You have created a new team",
#                 actionable=False
#             )
#             messages.add_message(request, messages.SUCCESS, f"Created Team: {titleCleaned}!")
#             return redirect('dashboard')
#         else:
#             messages.add_message(request, messages.ERROR, "Unable to create team")
#             return render(request, 'create_team.html', {'form': form})
#     else:
#         form = TeamForm()
#         return render(request, 'create_team.html', {'form': form})

class CreateTeamView(LoginRequiredMixin, CreateView):
    """ Class-based generic view for new team handling """

    model = Team
    template_name = 'create_team.html'
    form_class = TeamForm
    http_method_names = ['post', 'get']

    def form_valid(self, form):
        current_user = self.request.user
        form.instance.author = current_user
        response = super().form_valid(form)
        titleCleaned = form.cleaned_data.get("title")
        self.object.members.add(current_user)
        notification = Notification.objects.create(
            user=current_user,
            title="New Team Created: " + titleCleaned,
            description="You have created a new team",
            actionable=False
        )
        messages.add_message(self.request, messages.SUCCESS, f"Created Team: {titleCleaned}!")
        return response

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "Unable to create team")
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('dashboard')

@login_prohibited
def home(request):
    """Display the application's start/home screen."""
    return render(request, 'home.html')

@login_required
@team_member_prohibited_to_view_team
def show_team(request, team_id):
    """Show the team details: team name, description, members"""
    try:
        members, current_team, tasks = calculate_task_complete_score(team_id)
        unarchived_tasks = tasks.filter(is_archived=False)
        archived_tasks = tasks.filter(is_archived=True)

    except ObjectDoesNotExist:
        return redirect('dashboard')

    else:
        return render(request, 'show_team.html', {'team': current_team, 'unarchived': unarchived_tasks, 'archived': archived_tasks, 'members': members})

# @login_required
# @team_member_prohibited_to_view_team
# def create_task(request, team_id):
#     """Allow the user to create a Task for their Team"""
#     if request.method == "POST":
#         current_team = Team.objects.get(id = team_id)
#         form = TaskForm(request.POST)
#         if form.is_valid():
#             titleCleaned = form.cleaned_data.get("title")
#             descriptionCleaned = form.cleaned_data.get('description')
#             dueDateCleaned = form.cleaned_data.get("due_date")
#             task = Task.objects.create(author=current_team, title = titleCleaned, description=descriptionCleaned, due_date=dueDateCleaned)
#             messages.add_message(request, messages.SUCCESS, "Successfully created task")
#             return redirect('show_team', team_id)
#         else:
#             messages.add_message(request, messages.ERROR, "Unable to create task!")
#             return render(request, 'create_task.html', {'team': current_team,'form': form})
#     else:
#         form = TaskForm()
#         current_team = Team.objects.get(id = team_id)
#         return render(request, 'create_task.html', {'team': current_team,'form': form})

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

class CreateTaskView(LoginRequiredMixin, TeamMemberProhibitedMixin, CreateView):
    """ Class-based generic view for new task handling """

    model = Task
    template_name = 'create_task.html'
    form_class = TaskForm
    http_method_names = ['post', 'get']
    context_object_name = "task"
    pk_url_kwarg = 'team_id'
    redirect_if_not_team_member = 'dashboard'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        team_id = self.kwargs['team_id']
        context['team'] = Team.objects.get(id=team_id)
        return context

    def form_valid(self, form):
        team_id = self.kwargs['team_id']
        current_team = Team.objects.get(id=team_id)
        form.instance.author = current_team
        messages.add_message(self.request, messages.SUCCESS, "Successfully created task")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "Unable to create task!")
        return super().form_invalid(form)

    def get_success_url(self):
        team_id = self.kwargs['team_id']
        return reverse('show_team', kwargs={'team_id': team_id})
          
# @login_required
# @team_member_prohibited_to_customise_task
# def edit_task(request, task_id):
#     current_task = Task.objects.get(id=task_id)
#     current_team = current_task.author
#     if request.method == 'POST':
#         form = TaskForm(instance=current_task, data=request.POST)
#         if form.is_valid():
#             form.save()
#             messages.add_message(request, messages.SUCCESS, "Task Updated!")
#             return redirect('show_team', current_team.id)
#         else:
#             messages.add_message(request, messages.ERROR, "Unable to edit task!")
#     else:
#         form = TaskForm(instance=current_task)
#     return render(request, 'edit_task.html', {'task': current_task, 'form': form})

class EditTaskView(LoginRequiredMixin, TeamMemberProhibitedMixin, UpdateView):
    """ Class-based generic view for edit task handling """

    model = Task
    template_name = 'edit_task.html'
    form_class = TaskForm
    http_method_names = ['post', 'get']
    context_object_name = "task"
    pk_url_kwarg = 'task_id'
    redirect_if_not_team_member = 'dashboard'

    def get_object(self):
        task_id = self.kwargs['task_id']
        task = Task.objects.get(id=task_id)
        return task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_id = self.kwargs['task_id']
        current_task = Task.objects.get(id=task_id)
        context['task'] = current_task
        context['team'] = Team.objects.get(id=current_task.author.id)
        return context

    def get_success_url(self):
        task_id = self.kwargs['task_id']
        current_task = Task.objects.get(id=task_id)
        team_id = current_task.author.id
        return reverse('show_team', kwargs={'team_id': team_id})

# @login_required
# @team_member_prohibited_to_customise_task
# def delete_task(request, task_id):
#     current_user = request.user
#     current_task = Task.objects.get(id=task_id)
#     current_team = current_task.author
#     if current_task.author == current_team:
#         if current_team.author == current_user:
#             current_task.delete()
#             messages.add_message(request, messages.SUCCESS, "Task deleted!")
#         else:
#             messages.add_message(request, messages.ERROR, "You cannot delete a Task in a Team you did not create")
#     else:
#         messages.add_message(request, messages.ERROR, "You cannot delete another Teams Task")
#     return redirect('show_team', current_team.id)

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

class DeleteTaskView(LoginRequiredMixin, TeamAuthorProhibitedMixin, DeleteView):
    """ Class-based generic view for delete task handling """

    model = Task
    http_method_names = ['post']
    context_object_name = "task"
    pk_url_kwarg = 'task_id'
    redirect_if_not_team_author = 'dashboard'

    def get_object(self):
        task_id = self.kwargs['task_id']
        task = Task.objects.get(id=task_id)
        return task

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        task_id = self.kwargs['task_id']
        current_task = Task.objects.get(id=task_id)
        context['task'] = current_task
        context['team'] = Team.objects.get(id=current_task.author.id)
        return context

    def get_success_url(self):
        task_id = self.kwargs['task_id']
        current_task = Task.objects.get(id=task_id)
        team_id = current_task.author.id
        return reverse('show_team', kwargs={'team_id': team_id})

@login_required
@team_member_prohibited_to_customise_task
def toggle_task_status(request, task_id):
    current_user = request.user
    try:
        task_to_toggle = Task.objects.get(id=task_id)
        current_team = task_to_toggle.author
        task_to_toggle.toggle_task_status()
        task_to_toggle.save()
        messages.add_message(request, messages.SUCCESS, "Task status changed!")

    except ObjectDoesNotExist:
        return redirect('dashboard')

    else:
        return redirect('leaderboard', current_team.id)

@login_required
@team_member_prohibited_to_customise_task
def toggle_task_archive(request, task_id):
    current_user = request.user
    try:
        task_to_toggle = Task.objects.get(id=task_id)
        current_team = task_to_toggle.author
        task_to_toggle.toggle_archive()
        task_to_toggle.save()
        if task_to_toggle.is_archived :
            messages.add_message(request, messages.SUCCESS, "Task archived!")

        else:
            messages.add_message(request, messages.SUCCESS, "Task unarchived!")

    except ObjectDoesNotExist:
        return redirect('dashboard')

    else:
        return redirect('show_team', current_team.id)

@login_required
@team_member_prohibited_to_view_team
def leaderboard_view(request, team_id):
    try:
        members, current_team, tasks = calculate_task_complete_score(team_id)
        return redirect('show_team', current_team.id)

    except ObjectDoesNotExist:
        return redirect('dashboard')

@login_required
@team_member_prohibited_to_view_team
def assign_member_to_task(request, task_id, user_id):
    current_logged_in_user = request.user
    current_task = Task.objects.get(id=task_id)
    current_team = current_task.author
    selected_user = User.objects.get(id = user_id)
    if selected_user in current_team.members.all():
        if selected_user in current_task.assigned_members.all():
            current_task.assigned_members.remove(selected_user)
            messages.add_message(request, messages.WARNING, f"Removed {selected_user.full_name()}")
        else:
            current_task.assigned_members.add(selected_user)
            messages.add_message(request, messages.INFO, f"Added {selected_user.full_name()}")

    return redirect('show_team', current_team.id)

@login_required
@team_member_prohibited_to_view_team
def invite(request, team_id):
    team = get_object_or_404(Team, pk=team_id)

    if request.user != team.author:
        messages.error(request, "You do not have permission to invite members to this team.")
        return redirect('show_team', team_id=team_id)

    form = TeamInviteForm(request.POST or None, team=team)

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
    try:
        notification = Notification.objects.get(user=request.user, invitation=invitation)
        notification.delete()
    except Notification.DoesNotExist:
        redirect('dashboard')
    Notification.objects.create(
                user=request.user,
                title=f"Joined a team",
                description=f"You have joined {invitation.team.title}",
                actionable=False)

    messages.success(request, "You have joined the team!")
    return redirect('notifications')

@login_required
def decline_invitation(request, invitation_id):
    invitation = get_object_or_404(Invitation, pk=invitation_id, email=request.user.email)

    if invitation.status != Invitation.DECLINED:
        invitation.status = Invitation.DECLINED
        invitation.save()
        try:
            notification = Notification.objects.get(user=request.user, invitation=invitation)
            notification.delete()
        except Notification.DoesNotExist:
            redirect('dashboard')

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
            messages.add_message(request, messages.SUCCESS, "You have successfully Logged in!")
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
    messages.add_message(request, messages.SUCCESS, "You have signed out")
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


class TeamUpdateView(LoginRequiredMixin, TeamAuthorProhibitedMixin, UpdateView):
    """Display team editing screen, and handle team details modifications."""

    model = Team
    template_name = "edit_team.html"
    form_class = TeamForm
    redirect_if_not_team_author = 'dashboard'

    def get_object(self):
        """Return the object (team) to be updated."""
        team_id = self.kwargs['team_id']
        team = Team.objects.get(id=team_id)
        return team
    
    def get_success_url(self):
        """Return redirect URL after successful update."""
        messages.add_message(self.request, messages.SUCCESS, "Team updated!")
        return reverse(settings.REDIRECT_URL_WHEN_LOGGED_IN)

@login_required
@team_member_prohibited_to_view_team
def team_delete(request, team_id):
    try:
        team = Team.objects.get(id=team_id)
        if request.method == 'POST':        
            team.delete()                     
            return redirect('/') 
    except ObjectDoesNotExist:
        return redirect('dashboard')  

    return render(request, 'show_team.html', {'team': team})

@login_required
@team_member_prohibited_to_view_team
def leaderboard_view(request, team_id):
    try:
        members, current_team, tasks = calculate_task_complete_score(team_id)
        return redirect('show_team', current_team.id)

    except ObjectDoesNotExist:
        return redirect('dashboard')
    else:
        return redirect('show_team', team.id)

    
@login_required
def notifications(request):
    """Display Notifications associated with the user, including invitations."""
    invitations = Invitation.objects.filter(email=request.user.email, status=Invitation.INVITED)
    for invitation in invitations:
        if not Notification.objects.filter(user=request.user, invitation=invitation).exists():
            Notification.objects.create(
                user=request.user,
                title=f"Invitation to join {invitation.team.title}",
                description="",
                actionable=True,
                invitation=invitation
            )
    user_notifications = Notification.objects.filter(user=request.user)
    return render(request, 'notifications.html', {'user_notifications': user_notifications})

@login_required
def seen_notification(request, notification_id):
    current_user = request.user
    notification = Notification.objects.get(id=notification_id)
    if (notification.user == current_user):
        notification.mark_as_seen()
        notification.save()
        messages.add_message(request, messages.SUCCESS, "Marked as seen")
    else:
        return redirect('dashboard')
    return redirect('notifications')


def unseen_notifications(request):
    unseen_notifs = []
    if request.user.is_authenticated:
        unseen_notifs = Notification.objects.filter(user=request.user, seen=False)
    
    return {'unseen_notifs': unseen_notifs}