# Generated by Django 5.1.1 on 2024-11-14 19:54

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stocks', '0008_rename_platform_commission_product_platform_comission'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='platform_comission',
            new_name='platform_commission',
        ),
    ]
