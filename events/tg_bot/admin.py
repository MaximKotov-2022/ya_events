from django.contrib import admin

from .forms import ProfileForm
from .models import Profile, Subscription


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'external_id', 'name')
    form = ProfileForm


@admin.register(Subscription)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'profile', 'subscription', 'created_at')
