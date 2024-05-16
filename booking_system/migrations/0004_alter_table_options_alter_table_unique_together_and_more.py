# Generated by Django 5.0.6 on 2024-05-16 07:17

import booking_system.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_system', '0003_alter_table_options_table_status_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='table',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='table',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='reservation',
            name='end_time',
            field=models.TimeField(default=booking_system.models.get_midnight),
        ),
        migrations.AddField(
            model_name='reservation',
            name='start_time',
            field=models.TimeField(default=booking_system.models.get_midnight),
        ),
    ]