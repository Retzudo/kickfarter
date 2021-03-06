from django import forms
from django.utils.translation import ugettext_lazy as _
from app.models import User, Project


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(
            label=_("Password"),
            widget=forms.PasswordInput
    )

    password2 = forms.CharField(
            label=_("Repeat password"),
            widget=forms.PasswordInput,
            help_text=_("Enter the same password as before, for verification.")
    )

    class Meta:
        model = User
        fields = ('email',)

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
            )
        self.instance.email = self.cleaned_data.get('email')
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email = forms.EmailField(
        label=_('Email address'),
        widget=forms.TextInput(attrs={'placeholder': _('user@example.com')})
    )
    password = forms.CharField(
        label=_('Password'),
        widget=forms.PasswordInput(attrs={'placeholder': _('Password')}),
    )


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'currency', 'goal', 'cover_image']

        labels = {
            'title': _('Project title'),
            'description': _('Project description'),
        }

        widgets = {
            'title': forms.TextInput(attrs={'placeholder': _('My shitty project')}),
            'description': forms.Textarea(attrs={'placeholder': _('Describe your project')}),
            'goal': forms.NumberInput(attrs={'placeholder': _('10.00')}),
        }
