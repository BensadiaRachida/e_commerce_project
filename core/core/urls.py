"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include , re_path
from rest_framework.routers import DefaultRouter
from api import views
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'products', views.ProductViewSet, basename='product')
router.register(r'reviews', views.ReviewViewSet, basename='review')
router.register(r'checkouts', views.CheckoutViewSet, basename='checkout')
router.register(r'orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path("admin/", admin.site.urls),
    # include viewsets routes
    path("api/", include(router.urls)),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path(
        "api/auth/verify_email/",
        views.VerifyEmailCode.as_view(),
        name="VerifyEmailCode",
    ),
    path('api/user-checkouts/', views.UserCheckoutsView.as_view(), name='user-checkouts'),
    path('api/create-checkout-with-orders/', views.CreateCheckoutWithOrdersView.as_view(), name='create-checkout-with-orders')
    # path('api/change-password/', ChangePasswordView.as_view(), name='change-password'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)