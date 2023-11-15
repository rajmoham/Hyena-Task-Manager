from django.conf import settings
from django.shortcuts import redirect

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_invitation(to_email, code, team):
    from_email = settings.DEFAULT_FROM_EMAIL
    accept_url = settings.ACCEPT_URL

    subject = "Invitation to Task Manager"
    text_content = "Invitation to Task Manager. Your code is: %s" %code
    html_content = render_to_string('invitation_email.html', {'code':code , 'team': team, 'accept_url' : accept_url})

    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

def send_invitation_accepted(to_email,team, invitation):
    from_email = settings.DEFAULT_FROM_EMAIL
    subject = "Invitation accepted"
    text_content = "Your invitation was accepted"
    html_content = render_to_string("email_accepted_invitation.html", {'team':team, 'invitation' : invitation})
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, 'text/html')
    msg.send()

def login_prohibited(view_function):
    """Decorator for view functions that redirect users away if they are logged in."""

    def modified_view_function(request):
        if request.user.is_authenticated:
            return redirect(settings.REDIRECT_URL_WHEN_LOGGED_IN)
        else:
            return view_function(request)
    return modified_view_function
