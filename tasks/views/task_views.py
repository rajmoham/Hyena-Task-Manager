from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic.edit import UpdateView, DeleteView, CreateView
from django.urls import reverse
from tasks.forms import TaskForm
from tasks.helpers import team_member_prohibited_to_view_team
from django.db.models import Q
from tasks.models import Team, Task, User
from django.core.exceptions import ObjectDoesNotExist
from .mixins import TeamMemberProhibitedMixin, TeamAuthorProhibitedMixin

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
    
    def form_valid(self, form):
        messages.add_message(self.request, messages.SUCCESS, "Task Updated!")  # Add success message
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.add_message(self.request, messages.ERROR, "Unable to edit task!")  # Add error message
        return super().form_invalid(form)

    def get_success_url(self):
        task_id = self.kwargs['task_id']
        current_task = Task.objects.get(id=task_id)
        team_id = current_task.author.id
        return reverse('show_team', kwargs={'team_id': team_id})
    
class DeleteTaskView(LoginRequiredMixin, TeamAuthorProhibitedMixin, DeleteView):
    """ Class-based generic view for delete task handling """

    model = Task
    http_method_names = ['post', 'get']
    context_object_name = "task"
    pk_url_kwarg = 'task_id'
    redirect_if_not_team_author = 'dashboard'

    def get_object(self):
        task_id = self.kwargs['task_id']
        task = Task.objects.get(id=task_id)
        return task

    def get(self, request, *args, **kwargs):
        task_id = self.kwargs['task_id']
        current_task = Task.objects.get(id=task_id)
        team_id = current_task.author.id
        messages.add_message(self.request, messages.ERROR, "GET requests are not allowed. Please use the provided button.")
        return redirect('show_team', team_id=team_id)

    def get_success_url(self):
        task_id = self.kwargs['task_id']
        current_task = Task.objects.get(id=task_id)
        team_id = current_task.author.id
        messages.add_message(self.request, messages.SUCCESS, "Task deleted!")
        return reverse('show_team', kwargs={'team_id': team_id})
    
@login_required
@team_member_prohibited_to_view_team
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
@team_member_prohibited_to_view_team
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