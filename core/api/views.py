from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from .models import User, EmailConfirmationCode
from rest_framework.views import APIView
import json
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class VerifyEmailCode(APIView):
    permission_classes = []
    # email verification rest api view
    def post(self, request):
        """
        email verification rest API view:
        receives a code in a JSON post request,
        check if it's valid or not,
        if it's valid it confirms that the user has a valid email,
        else it returns an error message
        """
        if request.method == "POST":
            # user input
            post_request = json.loads(request.body)
            code = post_request["code"]
            if len(code) == 6:
                try:
                    # verify user input is the right code
                    user_email_code = EmailConfirmationCode.objects.get(code=code)
                    # check not None
                    if user_email_code:
                        user_email_code.user.is_active = True
                        user_email_code.user.save()
                        user_email_code.delete()
                        # return 
                        return Response(
                            "Email confirmed",
                            status=status.HTTP_200_OK,
                        )
                except EmailConfirmationCode.DoesNotExist:
                    raise NotFound()
            # set status code to indicate error to clients
            return Response(
                {"message": "error", "value": "not a valid code"},
                status=status.HTTP_400_BAD_REQUEST,
            )