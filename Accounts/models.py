from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager, Group, Permission
from datetime import datetime, timezone

class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and save a regular user with the given email and password.
        """
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """
        Create and save a superuser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("SuperUser must have is_staff=True")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("SuperUser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    objects = CustomUserManager()  

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

class PendingUser(models.Model):  
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    verification_code = models.CharField(max_length=50)  
    created_at = models.DateTimeField(auto_now_add=True)  

    def is_valid(self) -> bool:
        lifespan_in_seconds = 20 * 60  # 20 minutes
        now = datetime.now(timezone.utc)

        timediff = now - self.created_at
        timediff = timediff.total_seconds()

        return timediff <= lifespan_in_seconds
