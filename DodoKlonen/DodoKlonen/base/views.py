from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CreateDodoForm, CreateUpdateForm, UpdateForm
from .models import Profile, Update, UserDodoUpdate, Dodo, DodoApproval
from django.db import IntegrityError
from .forms import ProfileForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from datetime import date

# Create your views here.

def index(request):
    return render(request, "base/index.html")


@staff_member_required
def add_dodo(request):
    if request.method == 'POST':
        form = CreateDodoForm(request.POST)
        if form.is_valid():
            form.save()

            return redirect('newsfeed')  
    else:
        form = CreateDodoForm()
    return render(request, 'base/add_dodo.html', {'form': form})


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
    return redirect('newsfeed')

@login_required
def profile(request):
    user_profile = request.user.profile
    user_updates = Update.objects.filter(user=request.user)
    context = {'user_profile': user_profile, 'user_updates': user_updates}
    return render(request, 'base/profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    return render(request, 'base/edit_profile.html', {'form': form})

@login_required
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

@login_required
def add_update(request, dodo_name):
    dodo = get_object_or_404(Dodo, name=dodo_name)
    if request.method == 'POST':
        form = CreateUpdateForm(request.POST)
        if form.is_valid():
            update = form.save(commit=False)
            update.dodo = dodo  
            if dodo.alive:
                user_dodo_update, created = UserDodoUpdate.objects.get_or_create(user=request.user, dodo=dodo)
                if not created and user_dodo_update.last_updated >= timezone.now() - timezone.timedelta(days=1):
                    messages.error(request, "You can't make a second update on the same dodo on the same day.")
                else:
                    update.user = request.user
                    update.save()
                    user_dodo_update.last_updated = timezone.now()
                    user_dodo_update.save()
                    return redirect('dodo_details', dodo_name=dodo_name)
            else:
                messages.error(request, "You can only make updates on living dodos.")
        else:
            messages.error(request, "Adding an update has failed.")
    else:
        form = CreateUpdateForm(initial={'dodo': dodo})  
    return render(request, 'base/add_update.html', {'form': form, 'dodo': dodo})


@login_required
def delete_update(request, update_id):
    update = get_object_or_404(Update, id=update_id)
    if request.method == 'POST':
        update.delete()
        return redirect('profile') 
    return render(request, 'base/profile.html', {'update': update})


@login_required
def edit_update(request, update_id):
    update = get_object_or_404(Update, id=update_id)
    
    if request.method == 'POST':
        form = UpdateForm(request.POST, instance=update)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UpdateForm(instance=update)
    return render(request, 'base/edit_update.html', {'form': form})

from collections import defaultdict

@login_required
def newsfeed(request):

    all_dodos = Dodo.objects.all()
    dodo_names = [update.dodo.name for update in Update.objects.all()]

    updates_by_dodo = {}

    for dodo_name in dodo_names:
        updates = Update.objects.filter(dodo__name=dodo_name)
        updates_by_dodo[dodo_name] = updates

    context = {
        'updates_by_dodo': updates_by_dodo,
        'all_dodos': all_dodos,
    }

    return render(request, 'base/newsfeed.html', context)

def dodo_details(request, dodo_name):
    dodo = get_object_or_404(Dodo, name=dodo_name)
    dodo_updates = Update.objects.filter(dodo=dodo)
    today = date.today()
    age = today.year - dodo.date_of_birth.year - ((today.month, today.day) < (dodo.date_of_birth.month, dodo.date_of_birth.day))
    return render(request, 'base/dodo_details.html', {'dodo': dodo, 'dodo_updates': dodo_updates, 'age': age})


@login_required
def mark_as_dead(request, dodo_name):
    dodo = get_object_or_404(Dodo, name=dodo_name)
    
    if request.user.is_staff:  
        dodo.dead_approved = True 
        dodo.dead_approved_by = request.user  
        dodo.alive = False  
        dodo.save()
        messages.success(request, f"The dodo '{dodo.name}' has been marked as dead and approved.")
        return redirect('dodo_details', dodo_name=dodo_name)
    else:
        approval, created = DodoApproval.objects.get_or_create(dodo=dodo)
        if not dodo.dead_approved and not approval.pending_dead_approval: 
            approval.pending_dead_approval = True
            approval.save()
            return redirect('dodo_details', dodo_name=dodo_name)
        elif approval.pending_dead_approval:
            messages.error(request, "This dodo is already marked as pending approval.")
        else:
            messages.error(request, "This dodo has already been approved as dead.")
        return redirect('dodo_details', dodo_name=dodo_name)

@staff_member_required
def unapproved_dodos(request):
    if request.user.is_staff:
        unapproved_dodos = Dodo.objects.filter(dodoapproval__pending_dead_approval=True)
        return render(request, 'base/unapproved_dodos.html', {'unapproved_dodos': unapproved_dodos})
    else:
        return redirect('newsfeed') 

@staff_member_required
def approve_dodo(request, dodo_name):
    if request.user.is_staff:
        dodo = get_object_or_404(Dodo, name=dodo_name)
        approval = get_object_or_404(DodoApproval, dodo=dodo)
        approval.pending_dead_approval = False
        approval.save()
        dodo.dead_approved = True
        dodo.alive = False
        dodo.dead_approved_by = request.user
        dodo.save()
        return redirect('dodo_details', dodo_name=dodo_name)
    else:
        return redirect('newsfeed')  

@staff_member_required
def reject_dodo(request, dodo_name):
    if request.user.is_staff:
        dodo = get_object_or_404(Dodo, name=dodo_name)
        approval = get_object_or_404(DodoApproval, dodo=dodo)
        approval.pending_dead_approval = False
        approval.save()
        return redirect('unapproved_dodos')
    else:
        return redirect('newsfeed') 

@staff_member_required
def delete_all_updates(request, dodo_name):
    dodo = get_object_or_404(Dodo, name=dodo_name)
    Update.objects.filter(dodo=dodo).delete()
    return redirect('dodo_details', dodo_name=dodo_name)
