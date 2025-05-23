from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import PermissionsMixin
from django.db import models

from core.choices import GenderChoices

from shared.base_model import BaseModel
from shared.managers import CacheModelManager


class UserManager(BaseUserManager, CacheModelManager):
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field is required")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=password,
            **extra_fields,
        )
        user.save(using=self._db)

        return user

    def create_superuser(
        self, email, first_name, last_name, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, first_name, last_name, password, **extra_fields)

    def get_by_natural_key(self, email):
        return self.get(email=email)


class User(AbstractBaseUser, PermissionsMixin, BaseModel):
    username = models.CharField(max_length=50, unique=True, db_index=True)
    password = models.CharField(max_length=128, blank=True)
    new_password = models.CharField(max_length=128, blank=True)
    email = models.EmailField(unique=True, db_index=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return f"uid:{self.uid} {self.email}"

    def save(self, *args, **kwargs):
        if not self.pk:
            self.password = make_password(self.password)
            self.username = self.email if not self.username else self.username

        if self.new_password:
            self.password = make_password(self.new_password)
            self.new_password = ""

        super().save(*args, **kwargs)


class UserProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    photo = models.ImageField(upload_to="profile_pictures/", blank=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(
        max_length=20, choices=GenderChoices.choices, default=GenderChoices.NOT_SET
    )

    def __str__(self):
        return f"Profile of {self.user.email}"
