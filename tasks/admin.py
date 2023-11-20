from django.contrib import admin
from .models import User, Team, Invitation, Task

# Register your models here.
@admin.register(User) # our model we created
class UserAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for users."""

    # list of attributes we want to see in table of user models (in the table view of users)
    list_display = [
        'username', 'first_name', 'last_name', 'email', 'id', 'is_active',
    ]

@admin.register(Team) # our model we created
class TeamAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for teams."""

    # list of attributes we want to see in table of team models (in the table view of teams)
    list_display = [
        'title', 'description','id', 'display_members',
    ]

    def display_members(self, obj):
        return ", ".join([member.username for member in obj.members.all()])

    display_members.short_description = 'Members'


@admin.register(Invitation)
class InvitationAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for invitations."""

    # List of attributes you want to see in the table view of invitations
    list_display = [
        'team', 'email', 'status', 'date_sent'
    ]

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """Configuration of the admin interface for tasks."""

    # List of attributes you want to see in the table view of invitations
    list_display = [
        'author', 'title', 'description', 'created_at', 'due_date','id'
    ]

# from django.apps import apps
# from django.contrib import admin
# from django.contrib.auth.models import Group  # Import the Group model

# # Get a list of all installed models
# app_models = apps.get_models()

# # Exclude the Group model from the list
# models_to_register = [model for model in app_models if model is not Group]

# # Register all models except Group with the admin site
# for model in models_to_register:
#     admin.site.register(model)
