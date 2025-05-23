from django.db import models


class GenderChoices(models.TextChoices):
    MALE = "MALE", "Male"
    FEMALE = "FEMALE", "Female"
    OTHER = "OTHER", "Other"
    NOT_SPECIFIED = "NOT_SPECIFIED", "Not Specified"
    NOT_SET = "NOT_SET", "Not Set"
