from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from .models import *
from rest_framework.views import APIView
import json
from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework import viewsets, generics, permissions
from .serializers import *


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

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class ReviewViewSet(viewsets.ModelViewSet):
    queryset = review.objects.all()
    serializer_class = ReviewSerializer

class CheckoutViewSet(viewsets.ModelViewSet):
    queryset = Checkout.objects.all()
    serializer_class = CheckoutSerializer

class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

class UserCheckoutsView(generics.ListAPIView):
    serializer_class = CheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Checkout.objects.filter(user=user)

class CreateCheckoutWithOrdersView(generics.CreateAPIView):
    serializer_class = CheckoutSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data

        checkout_data = {
            "subtotal": data["subtotal"],
            "shipping_cost": data["shipping_cost"],
            "total": data["total"],
            "shipping_adress": data["shipping_adress"],
            "payment_method": data["payment_method"],
            "payment_status": data["payment_status"],
            "user": request.user.id
        }
        checkout_serializer = self.get_serializer(data=checkout_data)
        checkout_serializer.is_valid(raise_exception=True)
        self.perform_create(checkout_serializer)

        orders = data["orders"]
        for order_data in orders:
            order_data["user"] = request.user.id
            order_data["checkout"] = checkout_serializer.data["id"]

            order_serializer = OrderCreateSerializer(data=order_data)
            order_serializer.is_valid(raise_exception=True)
            order_serializer.save()

        headers = self.get_success_headers(checkout_serializer.data)
        return Response(checkout_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
