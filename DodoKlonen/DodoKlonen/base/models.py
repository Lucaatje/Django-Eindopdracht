from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime

# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    date_of_birth = models.DateField(null=True, blank=True)
    grade = models.CharField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username
    
class Dodo(models.Model):
    name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    alive = models.BooleanField(default=True)
    dead_approved = models.BooleanField(default=False)
    dead_approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Update(models.Model):
    dodo = models.ForeignKey(Dodo, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField()

    def __str__(self):
        return f"Update for {self.dodo.name} by {self.user.username} on {self.date}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class UserDodoUpdate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    dodo = models.ForeignKey(Dodo, on_delete=models.CASCADE)
    last_updated = models.DateTimeField(default=datetime.now)

    @staticmethod
    def can_add_update(user, dodo):
        last_update = UserDodoUpdate.objects.filter(user=user, dodo=dodo).first()
        if last_update:
            time_difference = datetime.now() - last_update.last_updated
            if time_difference.total_seconds() < 86400:  
                return False
        return True
    

class DodoApproval(models.Model):
    dodo = models.OneToOneField(Dodo, on_delete=models.CASCADE)
    pending_dead_approval = models.BooleanField(default=False)