# Generated by Django 5.0.5 on 2024-05-09 15:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_contact'),
    ]

    operations = [
        migrations.AddField(
            model_name='forgotpassword',
            name='expire_date',
            field=models.DateTimeField(default=datetime.datetime(2024, 5, 10, 15, 54, 11, 818204, tzinfo=datetime.timezone.utc)),
        ),
    ]
