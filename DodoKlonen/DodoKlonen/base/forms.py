from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile
from django.contrib.auth.forms import PasswordChangeForm

class CustomUserCreationForm(UserCreationForm):
    city = forms.CharField(max_length=100, required=True)
    date_of_birth = forms.DateField(help_text='Required. Format: YYYY-MM-DD')
    grade = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'city', 'date_of_birth', 'grade']

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['city', 'date_of_birth', 'grade']

class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if len(new_password1) < 8:
            raise forms.ValidationError("Het wachtwoord moet minimaal 8 tekens lang zijn.")
        return new_password1