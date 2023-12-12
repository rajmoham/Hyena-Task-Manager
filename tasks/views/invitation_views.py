from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from tasks.models import Notification, Invitation, Team
from tasks.helpers import team_member_prohibited_to_view_team
from tasks.forms import TeamInviteForm

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