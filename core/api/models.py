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




"""Email confirmation code model """

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

# phone number validator
    
phone_regex = RegexValidator(regex=r'^(05|06|07)[0-9]{8}$',
message=_('Invalid phone number ,phone number should be on the format : 05/06/07 (********)'))






class CustomUserManager(BaseUserManager):

    def create_user(self,email,first_name,last_name,phone,address,date_of_birth,sex,password=None,username=None):
        user=self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
            phone=phone,
            address=address,
            sex=sex,
            date_of_birth=date_of_birth,
            )
        
        user.set_password(password)
        # user.is_staff = False
        user.is_active=False
        user.save(using=self._db)
        return user

        
    def create_superuser(self, email, first_name,last_name,phone,date_of_birth,sex, password,username=None,adress=None,**extra_fields):
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
            address=None,
            date_of_birth=date_of_birth,
            sex=sex,
        )
        user.set_password(password)
        user.is_active=True
        user.is_staff=True
        user.is_superuser=True
        user.save(using=self._db)
        return user





""" User model """

class User(AbstractUser):
    username=models.CharField(max_length=10,null=True)
    email = models.EmailField("Email",unique=True)
    phone = models.CharField(max_length=10,validators=[phone_regex])
    address = models.CharField(max_length=300,blank=True,null=True)
    SEX = [("Male", "Male"), ("Female", "Female"), ("Other", "Other")]
    sex = models.CharField(max_length=30, choices=SEX, default="Male")
    date_of_birth = models.DateField(null= True,blank=True)
    profil_image=models.ImageField(null=True,upload_to='uploads/client_images')
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

    # The __str__() method is the default human-readable representation of the object. 
    # Django will use it in many places, such as the administration site.    

    def __str__(self):
        return f"{self.pk} : {self.first_name} {self.last_name} {self.email}"




""" Product model """

class Product(models.Model):
    CATEGORY_CHOICES = (
        ('electronics', 'Electronics'),
        ('phone', 'Phone'),
        ('bike', 'Bike'),
    )
    name=models.CharField(max_length=25)
    # textfield doesnt have a max length limit
    description=models.TextField()
    price=models.DecimalField(max_digits=10,decimal_places=2)
    discount=models.IntegerField()
    sale_price=models.DecimalField(max_digits=10,decimal_places=2)
    stock_quantity=models.IntegerField()
    categorie= models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    available=models.BooleanField(default=True)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)
    image = models.ImageField(upload_to='uploads/products/')

    @staticmethod
    def get_products_by_id(ids):
        return Products.objects.filter(id__in=ids)
  
    @staticmethod
    def get_all_products():
        return Product.objects.all()
  
    @staticmethod
    def get_all_products_by_category(category):
        if category:
            return Product.objects.filter(category=category)
        else:
            return Product.get_all_products()

    def get_reviews():
        return self.reviews.all()
    
    class Meta:
        verbose_name_plural = "Products"    

""" review model """

class review(models.Model):
    """
    ->Many-to-one relationship.
    -> related_name is used to access the 'review' instances. 
    ex:  product-instance.reviews.all()
    ->related_query_name ' enable you to use "review” as a lookup parameter in a queryset, 
     ex: Product.objects.filter(review='blabla').
   
    -> Here, a product can have none , or many reviews. 
   
    """
    content = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', related_query_name='review')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', related_query_name='review')
    created = models.DateField(auto_now_add=True)
    updated = models.DateField(auto_now=True)

    def __str__(self):
        return self.content
    class Meta:
        verbose_name_plural = "Reviews"    

""" checkout model """

class Checkout(models.Model):
    date_checkout= models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    #subtotal of the order, before shipping fees are added.
    subtotal= models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost= models.DecimalField(max_digits=10, decimal_places=2)
    # store the total cost of the order, including shipping.
    total= models.DecimalField(max_digits=10, decimal_places=2)
    shipping_adress= models.CharField(max_length=200)
    payment_method=models.CharField(max_length=25)
    STATUS=(
        ('paid', 'paid'),
        ('pending', 'pending'),
        ('cancelled', 'cancelled'),
    )
    payment_status=models.CharField(max_length=20,choices=STATUS,default='pending')
    user=models.ForeignKey(User,on_delete=models.CASCADE)

    def get_orders():
        return self.orders.all()
     
""" order model """

class Order(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='orders',related_query_name='order')
    quantity=models.IntegerField(default=1)  
    checkout=models.ForeignKey(Checkout,on_delete=models.CASCADE,related_name='orders',related_query_name='order',blank=True,null=True)

    @staticmethod
    def get_all_orders_by_user(user_id): 
        return Order.objects.filter(user=user_id)
    def __str__(self):
        return f"{self.product.name} : {self.quantity} "   

    class Meta:
        verbose_name_plural = "Orders"    

    



