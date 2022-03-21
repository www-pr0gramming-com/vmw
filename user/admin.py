from django.contrib import admin
from .models import CustomUser

from .forms import CustomUserCreationForm, CustomUserChangeForm


class CustomUserAdmin(admin.ModelAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = (
        "email",
        "stripe_customer_id",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    fieldsets = (
        ("Main", {"fields": ("email", "stripe_customer_id")}),
        # ("Personal info", {"fields": ("first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )

    # readonly_fields = (
    #     "last_login",
    #     "date_joined",
    # )

    # list_filter = (
    #     "email",
    #     "is_staff",
    #     "is_active",
    # )
    # search_fields = ("email",)
    # ordering = ("email",)


admin.site.register(CustomUser, CustomUserAdmin)
