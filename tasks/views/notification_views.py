from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from tasks.models import Notification, Invitation

@login_required
def notifications(request):
    """Display Notifications associated with the user, including invitations."""
    invitations = Invitation.objects.filter(email=request.user.email, status=Invitation.INVITED)
    for invitation in invitations:
        if not Notification.objects.filter(user=request.user, invitation=invitation).exists():
            notif = Notification.objects.create(
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