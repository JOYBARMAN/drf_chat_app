from django.contrib import admin

from core.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    model = User
    list_display = ["uid", "email", "last_login"]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Other",
            {
                "fields": (
                    "username",
                    "first_name",
                    "last_name",
                    "phone",
                    "uid",
                    "last_login",
                    "status",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
    )
    list_filter = [
        "status",
        "last_login",
    ]
    search_fields = ("phone", "email")
    readonly_fields = ("password", "uid", "last_login")
    list_select_related = True
    show_full_result_count = False
    ordering = ("-created_at",)
