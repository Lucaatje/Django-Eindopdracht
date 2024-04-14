from django.contrib import admin
from .models import Profile, Dodo, Update

# Register your models here.
admin.site.register(Profile)
admin.site.register(Dodo)
admin.site.register(Update)