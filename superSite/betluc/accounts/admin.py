from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur

# Register your models here.
admin.site.register(Utilisateur, UserAdmin)
