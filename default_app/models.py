from django.db import models
from accounts.models import CustomUser ,Listed_Vehicles 
# Create your models here.

class VehicleRating(models.Model):
    vehicle = models.ForeignKey(Listed_Vehicles, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)  
    comment=models.CharField(max_length=355,null=True,blank=True)
    rating = models.IntegerField()  

    def __str__(self):
        return f'{self.vehicle.name} - {self.user.username} - {self.rating}'
    



class Cart_Items(models.Model):
    user=models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    cart_item=models.ForeignKey(Listed_Vehicles, on_delete=models.CASCADE)

    

class Whishlist(models.Model):
    user=models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    wishlist_item=models.ForeignKey(Listed_Vehicles, on_delete=models.CASCADE)



class Coupon(models.Model):
    coupon_code=models.CharField(max_length=10,unique=True)
    coupon_discount=models.IntegerField()
    min_price=models.IntegerField(default=0,null=True,blank=True)