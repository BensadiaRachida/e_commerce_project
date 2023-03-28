from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer , PasswordResetSerializer , UserDetailsSerializer 
from rest_framework import serializers
from .models import *
from allauth.account.utils import setup_user_email
import django.contrib.auth.password_validation as validators
from django.core.exceptions import ValidationError
from email_validator import validate_email as VE , EmailNotValidError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

try:
    from allauth.account.adapter import get_adapter
    from allauth.utils import email_address_exists
except ImportError:
    raise ImportError('allauth needs to be added to INSTALLED_APPS.')


# this line retrieves the user model configured in settings as AUTH_USER_MODEL 
user=get_user_model()

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['__all__']

    
# Custom registration serializer
# django-rest-auth’s default register serializer (RegisterSerializer) only recognizes fields for django built-in user model
# the fields in the custom serializer are gonna appear in registration form in addition to the base user model fields (username , email ,psswd1,psswd2)
class CustomRegisterSerializer(RegisterSerializer):
   
    # validators

    phone_regex = RegexValidator(regex=r'^(5|6|7)[0-9]{8}$',message=_('Invalid phone number , phone number should be on the format : 5/6/7 (********)'))

    def validate_password(value):
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters long.')
        if not any(char.isdigit() for char in value):
            raise serializers.ValidationError('Password must contain at least one digit.')
        if not any(char.isalpha() for char in value):
            raise serializers.ValidationError('Password must contain at least one letter.')      
        return value
    username=serializers.CharField(required=False)
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    password1 = serializers.CharField( write_only=True, required=True,validators=[validate_password],style={'input_type': 'password', })
    password2 = serializers.CharField( write_only=True, required=True,style={'input_type': 'confirm password', })
    phone = serializers.CharField(max_length=10,required=True,validators=[phone_regex])
    date_of_birth = serializers.DateField(required=True, write_only=True)
    sex = serializers.CharField(required=True, write_only=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        try:
            emailobject=VE(email)
            email=emailobject.email
        except EmailNotValidError as errorMsg:
            raise ValidationError(_(str(errorMsg)))
            
    # If `email` is not valid
    # we print a human readable error message  
        if email and email_address_exists(email):
            raise ValidationError(_('A user is already registered with this e-mail address.'))
        return email  
    
    # password and password confirmation match validator

    def validate(self, data):
        if data['password1'].isdigit():
            raise serializers.ValidationError(
                _(" password must contain digits") )      
        if data['password1'] != data['password2']:
            raise serializers.ValidationError(
               _("The two password fields didn't match."))
        return data

    # the following two methods are instance methods of RegisterSerializer class , which we will override

    # clean the data

    def get_cleaned_data(self):
        super(CustomRegisterSerializer, self).get_cleaned_data()
        return {
            'first_name': self.validated_data.get('first_name', ''),
            'last_name': self.validated_data.get('last_name', ''),
            'email': self.validated_data.get('email', ''),
            'phone': self.validated_data.get('phone', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'date_of_birth': self.validated_data.get('date_of_birth', ''),
            'sex': self.validated_data.get('date_of_birth', ''),
        }
    # save a user instance

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        adapter.save_user(request, user, self)
        setup_user_email(request, user, [])
        user.phone = self.cleaned_data.get('phone')
        user.date_of_birth = self.cleaned_data.get('date_of_birth')
        user.sex = self.cleaned_data.get('sex')
        user.is_superuser = False
        user.save()
        return user

class CustomLoginSerializer(LoginSerializer): 
    pass


class VerifyEmailSerializer(serializers.Serializer):
   key = serializers.CharField()    
       
class ChangePasswordSerializer(serializers.Serializer):
    model = User

    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)   