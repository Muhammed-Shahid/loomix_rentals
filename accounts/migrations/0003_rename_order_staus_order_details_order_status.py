# Generated by Django 4.2.5 on 2023-10-05 06:34

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_order_details'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order_details',
            old_name='order_staus',
            new_name='order_status',
        ),
    ]
