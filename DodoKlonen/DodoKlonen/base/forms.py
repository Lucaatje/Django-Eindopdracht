from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile, Dodo, Update
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import timezone

def validate_date_of_birth(value):
    if value > timezone.now().date():
        raise forms.ValidationError("The date of birth cannot be in the future.")

class CustomUserCreationForm(UserCreationForm):
    city = forms.CharField(max_length=100, required=True)
    date_of_birth = forms.DateField(help_text='Required. Format: YYYY-MM-DD', validators=[validate_date_of_birth])
    grade = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2', 'city', 'date_of_birth', 'grade']

class ProfileForm(forms.ModelForm):
    date_of_birth = forms.DateField(validators=[validate_date_of_birth])

    class Meta:
        model = Profile
        fields = ['city', 'date_of_birth', 'grade']

class CustomPasswordChangeForm(PasswordChangeForm):
    def clean_new_password1(self):
        new_password1 = self.cleaned_data.get('new_password1')
        if len(new_password1) < 8:
            raise forms.ValidationError("Password must have at least 8 characters.")
        return new_password1

class CreateDodoForm(forms.ModelForm):
    name = forms.CharField(max_length=100, required=True)
    date_of_birth = forms.DateField(help_text='Format: YYYY-MM-DD', validators=[validate_date_of_birth])

    def clean_name(self):
        name = self.cleaned_data['name']
        if Dodo.objects.filter(name=name).exists():
            raise forms.ValidationError("A dodo with this name already exists.")
        return name

    class Meta:
        model = Dodo
        fields = ['name', 'date_of_birth']


class CreateUpdateForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea, max_length=200)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.initial_dodo = kwargs.pop('initial_dodo', None)  
        super(CreateUpdateForm, self).__init__(*args, **kwargs)
        if self.initial_dodo:
            self.fields['dodo'].initial = self.initial_dodo  

    def clean(self):
        cleaned_data = super().clean()
        dodo = cleaned_data.get('dodo')

        if dodo and not dodo.alive:
            raise forms.ValidationError("You can only create updates for dodos who are alive.")

        return cleaned_data

    def save(self, commit=True):
        instance = super(CreateUpdateForm, self).save(commit=False)
        instance.user = self.user
        if commit:
            instance.save()
        return instance

    class Meta:
        model = Update
        fields = ['dodo', 'description']


class UpdateForm(forms.ModelForm):
    description = forms.CharField(widget=forms.Textarea, max_length=200)
    dodo = forms.ModelChoiceField(queryset=Dodo.objects.filter(alive=True))

    class Meta:
        model = Update
        fields = ['dodo', 'description']
