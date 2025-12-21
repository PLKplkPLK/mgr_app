from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import CustomUser, Correction

# Register your models here.
# admin.site.register(CustomUser, UserAdmin)
admin.site.register(Correction)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Extra fields", {"fields": ("avatar", "score", "protector")}),
    )
