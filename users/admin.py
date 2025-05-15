from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Genre, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'User Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ()}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Genre)
admin.site.register(UserProfile)