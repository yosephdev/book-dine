# Generated by Django 5.0.6 on 2024-05-20 09:19

import booking_system.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_system', '0007_remove_reservation_start_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='start_time',
            field=models.TimeField(default=booking_system.models.get_midnight),
        ),
    ]
