"""Forms for the tasks app."""
from django import forms
from django.contrib.auth import authenticate
from django.core.validators import RegexValidator
from .models import User, Team, Invitation, Task
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

class LogInForm(forms.Form):
    """Form enabling registered users to log in."""

    username = forms.CharField(label="Username")
    password = forms.CharField(label="Password", widget=forms.PasswordInput())

    def get_user(self):
        """Returns authenticated user if possible."""

        user = None
        if self.is_valid():
            username = self.cleaned_data.get('username')
            password = self.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
        return user


class UserForm(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

class NewPasswordMixin(forms.Form):
    """Form mixing for new_password and password_confirmation fields."""

    new_password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(),
        validators=[RegexValidator(
            regex=r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[0-9]).*$',
            message='Password must contain an uppercase character, a lowercase '
                    'character and a number'
            )]
    )
    password_confirmation = forms.CharField(label='Password confirmation', widget=forms.PasswordInput())

    def clean(self):
        """Form mixing for new_password and password_confirmation fields."""

        super().clean()
        new_password = self.cleaned_data.get('new_password')
        password_confirmation = self.cleaned_data.get('password_confirmation')
        if new_password != password_confirmation:
            self.add_error('password_confirmation', 'Confirmation does not match password.')


class PasswordForm(NewPasswordMixin):
    """Form enabling users to change their password."""

    password = forms.CharField(label='Current password', widget=forms.PasswordInput())

    def __init__(self, user=None, **kwargs):
        """Construct new form instance with a user instance."""

        super().__init__(**kwargs)
        self.user = user

    def clean(self):
        """Clean the data and generate messages for any errors."""

        super().clean()
        password = self.cleaned_data.get('password')
        if self.user is not None:
            user = authenticate(username=self.user.username, password=password)
        else:
            user = None
        if user is None:
            self.add_error('password', "Password is invalid")

    def save(self):
        """Save the user's new password."""

        new_password = self.cleaned_data['new_password']
        if self.user is not None:
            self.user.set_password(new_password)
            self.user.save()
        return self.user


class SignUpForm(NewPasswordMixin, forms.ModelForm):
    """Form enabling unregistered users to sign up."""

    class Meta:
        """Form options."""

        model = User
        fields = ['first_name', 'last_name', 'username', 'email']

    def save(self):
        """Create a new user."""

        super().save(commit=False)
        user = User.objects.create_user(
            self.cleaned_data.get('username'),
            first_name=self.cleaned_data.get('first_name'),
            last_name=self.cleaned_data.get('last_name'),
            email=self.cleaned_data.get('email'),
            password=self.cleaned_data.get('new_password'),
        )
        return user

"""Form to ask user to create a Team. The Team author must be by the Team creator."""
class TeamForm(forms.ModelForm):
    class Meta:
        model = Team
        fields = ["title", 'description']
        widgets = {
            'description': forms.Textarea()
        }


class TeamEdit(forms.ModelForm):
    """Form to update user profiles."""

    class Meta:
        """Form options."""

        model = Team
        fields = ["title", 'description',]

class TeamInviteForm(forms.Form):
    email = forms.EmailField(
        label="Email Address",
        help_text="Enter the email address of the person you want to invite."
    )
    def __init__(self, *args, **kwargs):
        self.team = kwargs.pop('team', None)
        super(TeamInviteForm, self).__init__(*args, **kwargs)

    def clean_email(self):
        """Validate that the email is registered"""
        email = self.cleaned_data['email']
        if not User.objects.filter(email=email).exists():
            raise ValidationError("No user is registered with this email address.")
        user = User.objects.get(email=email)
        if self.team.members.filter(id=user.id).exists():
            raise forms.ValidationError("User already in the team.")
        if Invitation.objects.filter(team=self.team, email=email).exists():
            raise forms.ValidationError("This user has already been invited to the team.")

        return email

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", 'description', "due_date"]
        widgets = {
            'description': forms.Textarea(),
            'due_date': forms.TextInput(attrs={'type': 'datetime-local'}),
        }
        input_formats= {
            'due_date':'%Y-%m-%d T%H:%M',
        }
