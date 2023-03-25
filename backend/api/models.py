from django.db import models
from django.contrib.auth.models import AbstractUser
import datetime

class User(AbstractUser, models.Model):
    email = models.EmailField(unique=True)

    image = models.ImageField(upload_to="usersImages", blank=True)
    phone = models.CharField(max_length=50)
    date_of_birth = models.DateField(default=datetime.date.today)

    SEX = [("Male", "Male"), ("Female", "Female"), ("Other", "Other")]
    sex = models.CharField(max_length=30, choices=SEX, default="Male")

    created_on = models.DateTimeField(auto_now_add=True)
        
    class Meta:
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.pk} : {self.first_name} {self.last_name} {self.email}"
