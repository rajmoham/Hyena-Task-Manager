from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Q
from tasks.models import Team, Notification, Task
from django.shortcuts import render
from django.utils import timezone





@login_required
def dashboard(request):
    """Display the current user's dashboard."""
    current_user = request.user 
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