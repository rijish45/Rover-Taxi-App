from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

class Ride(models.Model):
    """Ride model"""
    owner = models.ForeignKey(
        User, related_name='rides_as_owner', 
        on_delete=models.CASCADE
    )
    driver = models.ForeignKey(
        User, related_name='rides_as_driver',  
        on_delete=models.DO_NOTHING,
        null=True, blank=True,
    )

    destination = models.CharField(max_length=1023)
    required_arrival_time = models.DateTimeField()
    passenger_number_from_owner = models.IntegerField()
    passenger_number_in_total = models.IntegerField()
    ride_status = models.CharField(max_length=255, default='open')

    requested_vehicle_type = models.CharField(max_length=255, blank=True)
    special_request = models.TextField(blank=True)
    
    can_be_shared = models.BooleanField(default=False)
    sharers = models.ManyToManyField(User, related_name='rides_as_sharer', blank=True)
    sharer_id_and_passenger_number_pair = JSONField(null=True, blank=True)

    def __str__(self):
        return f'{self.owner.first_name} {self.owner.last_name}'


