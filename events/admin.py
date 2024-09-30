from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import forms

from .models import Organisation, OrgUser, Event, PizzaOrder, PizzaSlices


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = OrgUser
        fields = ("contact",)


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = OrgUser
        fields = ('username', 'email', 'password1', 'password2', 'organisation', 'contact')

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            OrgUser.objects.get(username=username)
        except OrgUser.DoesNotExist:
            return username
        raise forms.ValidationError(self.error_messages['duplicate_username'])


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = OrgUser

    # Display fields in the user list view
    list_display = ["username", "organisation", "contact", "is_staff", "is_active"]

    # Filters for the list view
    list_filter = ["is_staff", "is_active"]

    # Form sections for changing user information
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Organisation info", {"fields": ("email", "organisation", "contact")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # Fields shown when adding a new user
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2", "organisation", "contact", "is_staff", "is_active")}
         ),
    )

    # Search and ordering for the admin list view
    search_fields = ("username", "email", "organisation", "contact")
    ordering = ("username",)


admin.site.register(Organisation, readonly_fields=['path'])
admin.site.register(OrgUser, CustomUserAdmin)
admin.site.register(Event)
admin.site.register(PizzaOrder)
admin.site.register(PizzaSlices)
