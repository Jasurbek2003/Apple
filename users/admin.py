from django.contrib import admin
from .models import Profile, Address


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number', 'created_at']
    search_fields = ['user__username', 'user__email', 'phone_number']


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user', 'address_type', 'is_default', 'full_name', 'city', 'country']
    list_filter = ['address_type', 'is_default', 'country']
    search_fields = ['user__username', 'full_name', 'address_line1', 'city', 'postal_code']