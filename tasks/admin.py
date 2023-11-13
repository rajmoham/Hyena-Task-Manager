from django.contrib import admin
from .models import User, Team

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


