# Generated by Django 5.0.6 on 2024-05-20 19:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_system', '0011_auto_20240520_1923'),
    ]

    operations = [
        migrations.AddField(
            model_name='restaurant',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
