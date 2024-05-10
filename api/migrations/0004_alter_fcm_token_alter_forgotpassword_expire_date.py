# Generated by Django 5.0.5 on 2024-05-10 02:51

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_forgotpassword_expire_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fcm',
            name='token',
            field=models.CharField(max_length=500, unique=True),
        ),
        migrations.AlterField(
            model_name='forgotpassword',
            name='expire_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 11, 2, 51, 23, 144428, tzinfo=datetime.timezone.utc)),
        ),
    ]
