# Generated by Django 2.1.7 on 2020-05-08 17:21

import User_Accounts.models
from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('User_Accounts', '0004_auto_20200507_2139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='users',
            name='id',
            field=models.UUIDField(default=uuid.UUID('32cb0d20-4c74-4fd9-b306-d9a3237bee51'), primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='users',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to=User_Accounts.models.image_path, verbose_name='profile_photo'),
        ),
    ]
