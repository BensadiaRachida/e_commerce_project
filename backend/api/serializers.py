from dj_rest_auth.registration.serializers import RegisterSerializer
from rest_framework import serializers
from allauth.account.utils import setup_user_email

try:
    from allauth.account.adapter import get_adapter
    from allauth.utils import email_address_exists
except ImportError:
    raise ImportError('allauth needs to be added to INSTALLED_APPS.')
    
# Custom registration serializer
class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(required=True, write_only=True)
    last_name = serializers.CharField(required=True, write_only=True)
    phone = serializers.CharField(max_length=30, required=True)
    date_of_birth = serializers.DateField(required=True, write_only=True)
    sex = serializers.CharField(required=True, write_only=True)

    def validate_email(self, email):
        email = get_adapter().clean_email(email)
        if email and email_address_exists(email):
            raise ValidationError409(_('A user is already registered with this e-mail address.'))
        return email

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