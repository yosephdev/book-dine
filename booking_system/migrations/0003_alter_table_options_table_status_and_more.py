# Generated by Django 5.0.6 on 2024-05-15 17:55

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_system', '0002_restaurant_rating'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='table',
            options={'ordering': ['table_number']},
        ),
        migrations.AddField(
            model_name='table',
            name='status',
            field=models.CharField(choices=[('available', 'Available'), ('reserved', 'Reserved'), ('occupied', 'Occupied')], default='available', max_length=20),
        ),
        migrations.AlterField(
            model_name='table',
            name='capacity',
            field=models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.AlterField(
            model_name='table',
            name='table_number',
            field=models.PositiveIntegerField(unique=True),
        ),
        migrations.AlterUniqueTogether(
            name='table',
            unique_together={('restaurant', 'table_number')},
        ),
    ]
