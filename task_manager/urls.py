"""
URL configuration for task_manager project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from tasks import views
from django.conf.urls import handler404

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('log_in/', views.LogInView.as_view(), name='log_in'),
    path('log_out/', views.log_out, name='log_out'),
    path('password/', views.PasswordView.as_view(), name='password'),
    path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
    path('sign_up/', views.SignUpView.as_view(), name='sign_up'),
    path('create_team/', views.create_team, name='create_team'),
    path('team/<int:team_id>', views.show_team, name='show_team'),
    path('team/<int:team_id>/invite/', views.invite, name='invite'),
    path('invitations/', views.list_invitations, name='list_invitations'),
    path('invitations/accept/<int:invitation_id>/', views.accept_invitation, name='accept_invitation'),
    path('invitations/decline/<int:invitation_id>/', views.decline_invitation, name='decline_invitation'),
    path('create_task/<int:team_id>', views.create_task, name="create_task" ),
    path('edit_team/', views.TeamUpdateView.as_view(), name='edit_team'),
    path('edit_task/<int:task_id>', views.edit_task, name='edit_task'),
]

handler404 = 'tasks.views.custom_404'
