from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from .models import Profile
from django.db import IntegrityError
from .forms import ProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages

# Create your views here.

def index(request):
    return render(request, "base/index.html")

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  
            try:
                Profile.objects.create(
                    user=user,
                    city=form.cleaned_data['city'],
                    date_of_birth=form.cleaned_data['date_of_birth'],
                    grade=form.cleaned_data['grade']
                )  
            except IntegrityError:
                profile = Profile.objects.get(user=user)
                profile.city = form.cleaned_data['city']
                profile.date_of_birth = form.cleaned_data['date_of_birth']
                profile.grade = form.cleaned_data['grade']
                profile.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def logoutview(request):
    logout(request)
    return redirect('index')

@login_required
def profile(request):
    user_profile = request.user.profile
    context = {'user_profile': user_profile}
    return render(request, 'base/profile.html', context)

def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'base/edit_profile.html', {'form': form})

def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated.')
            return redirect('profile')
        else:
            messages.error(request, 'Something goes wrong. Check your input.')
    else:
        form = PasswordChangeForm(user=request.user)
    return render(request, 'base/change_password.html', {'form': form})