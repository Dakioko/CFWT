from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('data_entry', 'Data Entry Personnel'),
        ('public', 'Public User'),
        ('validator', 'Validator'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='public')
    email = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
