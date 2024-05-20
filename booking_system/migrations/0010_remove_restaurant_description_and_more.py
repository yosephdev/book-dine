import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking_system', '0009_alter_reservation_end_time_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restaurant',
            name='description',
        ),
        migrations.RemoveField(
            model_name='restaurant',
            name='opening_hours',
        ),
        migrations.RemoveField(
            model_name='restaurant',
            name='phone_number',
        ),
        migrations.RemoveField(
            model_name='restaurant',
            name='website',
        ),
        migrations.AddField(
            model_name='restaurant',
            name='user',
            field=models.ForeignKey(null=True, blank=True, on_delete=django.db.models.deletion.CASCADE,
                                    related_name='owned_restaurants', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='restaurant',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='reservations', to='booking_system.restaurant'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='table',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='reservations', to='booking_system.table'),
        ),
        migrations.AlterField(
            model_name='reservation',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE,
                                    related_name='reservations', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='cuisine',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='restaurant',
            name='rating',
            field=models.DecimalField(decimal_places=2, max_digits=3),
        ),
        migrations.AlterField(
            model_name='table',
            name='capacity',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='table',
            name='status',
            field=models.CharField(
                choices=[('available', 'Available'), ('occupied', 'Occupied')], max_length=20),
        ),
        migrations.AlterField(
            model_name='table',
            name='table_number',
            field=models.CharField(max_length=10),
        ),
    ]
