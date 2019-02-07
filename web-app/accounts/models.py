from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class DriverProfile(models.Model):
    """Driver's Profile"""
    user = models.OneToOneField(User, related_name='driverProfile', on_delete=models.CASCADE)
    real_name = models.CharField(max_length=255, default='')
    vehicle_type = models.CharField(max_length=255, default='')
    license_plate_number = models.CharField(max_length=20, default='')
    maximum_passengers = models.IntegerField(default=0)
    special_vehicle_info = models.TextField(blank=True)
    is_driver = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.real_name}\'s Driver Profile'


@receiver(post_save, sender=User)
def create_driver_profile(sender, instance, created, **kwargs):
    if created:
        DriverProfile.objects.create(user=instance)



