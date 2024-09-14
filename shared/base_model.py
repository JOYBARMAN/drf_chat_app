import uuid

from django.db import models

from shared.choices import StatusChoices

from dirtyfields import DirtyFieldsMixin
from typing import Iterable

class BaseModel(DirtyFieldsMixin, models.Model):
    """Base class for all other models."""

    uid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        db_index=True,
        unique=True,
        help_text="Unique identifier for this model instance.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp indicating when the instance was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp indicating when the instance was last updated.",
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE,
        help_text="Status of the instance, typically used for soft deletion.",
    )

    @classmethod
    def get_active_instance(cls) -> Iterable:
        """Get active instance of the model."""
        return cls.objects.filter(status=StatusChoices.ACTIVE)

    class Meta:
        abstract = True