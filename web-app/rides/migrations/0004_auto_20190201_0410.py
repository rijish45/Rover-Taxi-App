# Generated by Django 2.1.5 on 2019-02-01 04:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rides', '0003_auto_20190201_0317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ride',
            name='driver',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='rides_as_driver', to=settings.AUTH_USER_MODEL),
        ),
    ]