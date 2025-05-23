from django.contrib import admin


class BaseModelAdmin(admin.ModelAdmin):
    """Base Model Admin with common fields from BaseModel."""

    readonly_fields = [
        "uid",
        "created_at",
        "updated_at",
        "status",
    ]

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + [
                "uid",
            ]
        return self.readonly_fields

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if "uid" not in list_display:
            return [
                "uid",
            ] + list_display
        return list_display
