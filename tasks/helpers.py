from django.conf import settings
from django.shortcuts import redirect
from .models import Team, Task, User
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

def team_member_prohibited_to_view_team(view_function):
    """ Decorator for view functions that redirect users away if they are not a team member of that team when they want to view team. """
    def modified_view_function(request, *args, **kwargs):
        current_user = request.user

        team_id = kwargs.get('team_id', None)
        task_id = kwargs.get('task_id', None)
        user_id = kwargs.get('user_id', None)

        current_team = None

        if team_id != None:
            try: 
                current_team = Team.objects.get(id=team_id)
            except ObjectDoesNotExist:
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

        if task_id != None:
            try: 
                current_task = Task.objects.get(id=task_id)
                current_team = Team.objects.get(id=current_task.author.id)
            except ObjectDoesNotExist:
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

        if current_user.is_authenticated and (current_user in current_team.members.all() or current_user == current_team.author):
            return view_function(request, *args, **kwargs)
        else:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

    return modified_view_function

def team_member_prohibited_to_customise_task(view_function):
    """ Decorator for view functions that redirect users away if they are not a team member of that team when they want to customise tasks. """
    def modified_view_function(request, *args, **kwargs):
        current_user = request.user

        team_id = kwargs.get('team_id', None)
        task_id = kwargs.get('task_id', None)
        user_id = kwargs.get('user_id', None)

        current_team = None

        if 'task_id' != None:
            try: 
                current_task = Task.objects.get(id=task_id)
                current_team = Team.objects.get(id=current_task.author.id)
            except ObjectDoesNotExist:
                return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

        # if 'user_id' is not None:
        #     try: 
        #         selected_user = User.objects.get(id=user_id)
        #     except ObjectDoesNotExist:
        #         return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)

        if current_user.is_authenticated and (current_user in current_team.members.all() or current_user == current_team.author):
            return view_function(request, *args, **kwargs)
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
    