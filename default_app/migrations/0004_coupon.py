# Generated by Django 4.2.5 on 2023-10-23 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('default_app', '0003_rename_cart_item_whishlist_wishlist_item'),
    ]

    operations = [
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coupon_discount', models.IntegerField()),
                ('min_price', models.ImageField(blank=True, default=0, null=True, upload_to='')),
            ],
        ),
    ]
