from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
    Permission,
    Group,
)
from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField
from .Order_Status import PaymentStatus
from django.core.validators import MinValueValidator




class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    phone = models.CharField(max_length=15)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)
    wallet_cash= models.IntegerField(validators=[MinValueValidator(0)], default=0)
    # Change the related_name to avoid clash
    groups = models.ManyToManyField(Group, blank=True, related_name="custom_users")
    user_permissions = models.ManyToManyField(
        Permission,
        blank=True,
        help_text="Specific permissions for this user.",
        related_name="custom_users",
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name", "phone"]

    # def __str__(self):
    #     return self.email
class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    license = models.CharField(max_length=50,null=True,blank=True)
    house_name = models.CharField(max_length=255)
    street = models.CharField(max_length=255)
    place = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    phone=models.CharField(max_length=15,null=True,blank=True)
    land_mark = models.CharField(max_length=255, blank=True, null=True)
    default_address=models.BooleanField(default=False)
    def __str__(self):
        return f"{self.house_name}, {self.city}, {self.state} {self.postal_code}, {self.city}"

class Listed_Vehicles(models.Model):
    vehicle_number = models.CharField(max_length=20)
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    transmission = models.CharField(max_length=30)
    varient = models.CharField(max_length=15)
    fuel_type = models.CharField(max_length=30)
    fuel_available = models.IntegerField()
    price = models.IntegerField()
    place = models.CharField(max_length=255)
    availability = models.BooleanField(default=True)
    rating = models.IntegerField(null=True, blank=True)
    review = models.CharField(max_length=300, null=True, blank=True)
    rc_book = models.ImageField(upload_to="vehicle_images")
    pollution_certificate = models.ImageField(upload_to="vehicle_images")
    exterior_image = models.ImageField(upload_to="vehicle_images")
    interior_image = models.ImageField(upload_to="vehicle_images")
    blocked = models.BooleanField(default=False)
    discount=models.IntegerField(null=True,blank=True)


class Order_Details(models.Model):
    product = models.IntegerField()
    customer = models.ForeignKey(CustomUser, on_delete=models.PROTECT)
    seller = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="seller",
        null=True,
        blank=True,
    )
    shipping_address=models.ForeignKey(Address,on_delete=models.PROTECT)
    payment_status = models.CharField(default=PaymentStatus.PENDING, max_length=250)
    order_date = models.DateTimeField()
    deliver_date = models.DateField()
    return_date = models.DateField()
    order_status = models.CharField(max_length=20)
    amount = models.IntegerField()
    payment_id = models.CharField(null=True, blank=True, default=0)


# class Order_Items(models.Model):
#     order_id
#     product_id=models.ForeignKey(Listed_Vehicles,on_delete=models.PROTECT)
