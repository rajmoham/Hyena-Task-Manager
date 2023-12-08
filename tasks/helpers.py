from django.conf import settings
from django.shortcuts import redirect
from .models import Team, Task
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404

def login_prohibited(view_function):
    """Decorator for view functions that redirect users away if they are logged in."""

    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function

def team_member_prohibited(view_function):
    """ Decorator for view functions that redirect users away if they are not a team member of that team. """
    def modified_view_function(request, team_id):
        current_user = request.user
        try: 
            current_team = Team.objects.get(id=team_id)
        except ObjectDoesNotExist:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

        if current_user.is_authenticated and (current_user in current_team.members.all() or current_user == current_team.author):
            return view_function(request, team_id=current_team.id)
        else:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    return modified_view_function

def calculate_task_complete_score(team_id):
    """ Helper function to calculate the tasks each user has completed."""
    try:
        current_team = Team.objects.get(pk=team_id)
        members = current_team.members.all()
        tasks = Task.objects.filter(author=current_team)
        for member in members:
            member.total_tasks_completed = 0
            for task in tasks:
                if task.is_complete and member in task.assigned_members.all():
                    member.total_tasks_completed += task.points
                    member.save()

        members = sorted(members, key=lambda m: m.total_tasks_completed, reverse=True)
        return members, current_team, tasks

    except ObjectDoesNotExist:
        raise Http404("Team does not exist")
    