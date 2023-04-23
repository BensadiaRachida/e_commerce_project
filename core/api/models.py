from django.db import models
from django.contrib.auth.models import AbstractUser,BaseUserManager
from django.core import validators
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
import datetime
from django.conf import settings
import hashlib
from os import urandom
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.models import Site

# Email confirmation code model
class EmailConfirmationCode(models.Model):
    """
    Email confirmation code model:
    to store codes that has been sent to users to validate their emails
    should be deleted when a user email gets validated
    """

    user = models.OneToOneField("User", on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_on = models.DateTimeField(auto_now_add=True)

    def send_email(self, code):
        subject = "Email Confirmation"
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL")
        to_email = [self.user.email]
        name = "Outrun"
        domain = Site.objects.get_current().domain
        body_html = render_to_string(
            "email_verification.html",
            {"code": str(code), "domain": domain, "user": self.user},
        )
        send_mail(subject, name, from_email, to_email, html_message=body_html)

    @classmethod
    def generate_otp(cls, length=6):
        m = hashlib.sha256()
        m.update(getattr(settings, "SECRET_KEY", None).encode("utf-8"))
        m.update(urandom(16))
        otp = str(int(m.hexdigest(), 16))[-length:]
        return otp

"""
    phone number validator
    
"""
phone_regex = RegexValidator(regex=r'^(05|06|07)[0-9]{8}$',
message=_('Invalid phone number ,phone number should be on the format : 05/06/07 (********)'))

class CustomUserManager(BaseUserManager):

    def create_user(self,email,first_name,last_name,phone,date_of_birth,sex,password=None,username=None):
        user=self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            sex=sex,
            date_of_birth=date_of_birth,
            )
        # if not image :
        #     user.image=None
        # else:      
        user.set_password(password)
        # user.is_staff = False
        user.is_active=False
        user.save(using=self._db)
        return user

        
    def create_superuser(self, email, first_name,last_name,phone,date_of_birth,sex, password,username=None,**extra_fields):
        if not email:
            raise ValueError("You must provide an email")
        if not password:
            raise ValueError("You must provide a password")
        if not first_name:
            raise ValueError("You must provide a first name")
        if not last_name :
            raise ValueError("You must provide a last name")    

        user = self.create_user(
            email=self.normalize_email(email),
            password=password,
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            date_of_birth=date_of_birth,
            sex=sex,
        )
        user.set_password(password)
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self._db)
        return user

class User(AbstractUser):
    username=models.CharField(max_length=10,null=True)
    email = models.EmailField("Email",unique=True)
    image = models.ImageField(upload_to="usersImages", blank=True, null = True ,max_length=100, verbose_name='client img')
    phone = models.CharField(max_length=10,validators=[phone_regex])
    SEX = [("Male", "Male"), ("Female", "Female"), ("Other", "Other")]
    sex = models.CharField(max_length=30, choices=SEX, default="Male")
    date_of_birth = models.DateField(null= True)
    # is_active=models.BooleanField(default=True)
    # is_staff=models.BooleanField(default=False)
    # is_admin=models.BooleanField(default=False)
    # is_superuser=models.BooleanField(default=False)
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['phone','date_of_birth','sex','first_name','last_name']
    # setting my custom user manager as the default user manager 
    # that takes care of creating user instances and saving them in database

    objects=CustomUserManager()

    def has_perm(self,perm,obj=None):
        return self.is_superuser
    def has_module_perms(self,app_label):
        return True    

 
    class Meta:
        verbose_name_plural = "Users"

    def __str__(self):
        return f"{self.pk} : {self.first_name} {self.last_name} {self.email}"