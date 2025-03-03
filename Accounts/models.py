from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager, Group, Permission
from common.models import BaseModel
# Create your models here.



class CustomUserManager(BaseUserManager):
    

    def create_user(self,email,username,password,**extra_fields):
        """
        create and save the user
        """
        if not email:
            raise ValueError("Email must be set ")
        user=self.model(email=email,**extra_fields )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self,email,username,password,**extra_fields):
        extra_fields.setdefault("is_staff",True)
        extra_fields.setdefault("is_superuser",True)
        extra_fields.setdefault("is_active",True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("SuperUser must have is_staff = True")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("SuperUser must have is_superuser = True")
        user=self.create_user(self,email,username,password,**extra_fields)
        user.save()


class User(AbstractBaseUser,PermissionsMixin):
    email=models.EmailField(unique=True)
    username=models.CharField(max_length=50)
    password=models.CharField(max_length=255)
    USERNAME_FIELD="email"
    REQUIRED_FIELDS=[]
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)

    groups = models.ManyToManyField(Group, related_name="custom_user_groups", blank=True)
    user_permissions = models.ManyToManyField(Permission, related_name="custom_user_permissions", blank=True)

    object=CustomUserManager()

import datetime
from datetime import timezone

class PendingUser(BaseModel):
    email=models.EmailField()
    username=models.CharField(max_length=50)
    password=models.CharField(max_length=255)
    varification_code=models.CharField(max_length=255)
    created_at=models.DateField(auto_now_add=True)

    def is_valid(self)-> bool:
        lifespan_in_seconds=20*60
        now=datetime.now(timezone.utc)


        timediff=now-self.created_at
        timediff=timediff.total_seconds()
        if timediff > lifespan_in_seconds:
            return False
        return True