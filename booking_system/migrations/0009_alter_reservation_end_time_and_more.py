# Generated by Django 5.0.6 on 2024-05-20 18:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_system', '0008_reservation_start_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='end_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='start_time',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='table',
            name='table_number',
            field=models.PositiveIntegerField(),
        ),
    ]
