# Generated by Django 2.1.5 on 2019-01-31 02:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_auto_20190131_0207'),
    ]

    operations = [
        migrations.AlterField(
            model_name='driverprofile',
            name='license_plate_number',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='driverprofile',
            name='maximum_passengers',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='driverprofile',
            name='vehicle_type',
            field=models.CharField(max_length=255),
        ),
    ]
