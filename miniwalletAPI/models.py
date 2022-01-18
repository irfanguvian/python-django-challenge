from pyexpat import model
from statistics import mode
from venv import create
from django.db import models
from django.contrib.auth.models import AbstractBaseUser

from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token


# Create your models here.


class Customer(AbstractBaseUser):
    id = models.CharField(max_length=255, unique=True, primary_key=True)

    USERNAME_FIELD = "id"

    def __str__(self):
        return self.id

    def has_perm(self, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

    def __str__(self):
        return self.id


class Wallet(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    owned_by = models.CharField(max_length=255)
    status = models.CharField(max_length=255, default="disable")
    enabled_at = models.DateTimeField(null=True, blank=True)
    disabled_at = models.DateTimeField(null=True, blank=True)
    balance = models.IntegerField()

    def __str__(self):
        return self.id


class Transaction(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    type = models.CharField(max_length=255, null=True, blank=True)
    withdrawn_by = models.CharField(max_length=255, null=True, blank=True)
    deposited_by = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=255)
    withdrawn_at = models.DateTimeField(null=True, blank=True)
    deposited_at = models.DateTimeField(null=True, blank=True)
    amount = models.IntegerField()
    reference_id = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.reference_id


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
