from django.db.models import TextChoices


class StatusChoices(TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
    DELETED = "DELETED", "Deleted"
    DRAFT = "DRAFT", "Draft"
    REMOVED = "REMOVED", "Removed"