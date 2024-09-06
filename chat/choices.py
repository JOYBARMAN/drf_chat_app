from django.db.models import TextChoices


class StatusChoices(TextChoices):
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
    DELETED = "DELETED", "Deleted"
    DRAFT = "DRAFT", "Draft"
    REMOVED = "REMOVED", "Removed"


class ReactionChoices(TextChoices):
    NONE = "NONE", "None"
    LIKE = "LIKE", "Like"
    DISLIKE = "DISLIKE", "Dislike"
    LAUGH = "LAUGH", "Laugh"
    SAD = "SAD", "Sad"
    CUTE = "CUTE", "Cute"
    LOVE = "LOVE", "Love"
    WOW = "WOW", "Wow"


class UserRoleChoices(TextChoices):
    ADMIN = "ADMIN", "Admin"
    CO_ADMIN = "CO_ADMIN", "Co Admin"
    MODERATOR = "MODERATOR", "Moderator"
    MEMBER = "MEMBER", "Member"
    VIEWER = "VIEWER", "Viewer"

class InvitationStatusChoices(TextChoices):
    PENDING = "PENDING", "Pending"
    ACCEPTED = "ACCEPTED", "Accepted"
    REJECTED = "REJECTED", "Rejected"
    CANCELLED = "CANCELLED", "Cancelled"