from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.core import validators
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import datetime
phone_regex = RegexValidator(regex=r'^(5|6|7)[0-9]{8}$',message=_('Invalid phone number ,phone number should be on the format : 5/6/7 (********)'))
class User(AbstractUser):
    username=models.CharField(max_length=15,unique=False,blank=True,null=True)
    email = models.EmailField("Email",unique=True)
    image = models.ImageField(upload_to="usersImages", blank=True, null = True ,max_length=100, verbose_name='client img')
    phone = models.CharField(max_length=9,validators=[phone_regex])
    SEX = [("Male", "Male"), ("Female", "Female"), ("Other", "Other")]
    sex = models.CharField(max_length=30, choices=SEX, default="Male")
    date_of_birth = models.DateField(null= True)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True)
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['phone','date_of_birth','sex','first_name','last_name']

        
    class Meta:
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.pk} : {self.first_name} {self.last_name} {self.email}"
