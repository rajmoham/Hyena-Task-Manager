from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse
from tasks.forms import TeamForm
from tasks.helpers import calculate_task_complete_score, team_member_prohibited_to_view_team
from tasks.models import Team, Notification
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from .mixins import TeamAuthorProhibitedMixin






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
    
class DeleteTeamView(LoginRequiredMixin, TeamAuthorProhibitedMixin, DeleteView):
    """ Class-based generic view for delete team handling """

    model = Team
    http_method_names = ['post', 'get']
    context_object_name = "team"
    pk_url_kwarg = 'team_id'
    redirect_if_not_team_author = 'dashboard'

    def get_object(self):
        team_id = self.kwargs['team_id']
        team = Team.objects.get(id=team_id)
        return team
    
    def get(self, request, *args, **kwargs):
        team_id = self.kwargs['team_id']
        current_team = Team.objects.get(id=team_id)
        messages.add_message(self.request, messages.ERROR, "GET requests are not allowed. Please use the provided button.")
        return redirect('show_team', team_id=team_id)

    def get_success_url(self):
        team_id = self.kwargs['team_id']
        current_team = Team.objects.get(id=team_id)
        messages.add_message(self.request, messages.SUCCESS, "Team deleted!")
        return reverse('dashboard')
        #return reverse(dashboard)

@login_required
@team_member_prohibited_to_view_team
def leaderboard_view(request, team_id):
    try:
        members, current_team, tasks = calculate_task_complete_score(team_id)
        return redirect('show_team', current_team.id)

    except ObjectDoesNotExist:
        return redirect('dashboard')