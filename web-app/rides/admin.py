from django.contrib import admin

from .models import Ride


class RideAdmin(admin.ModelAdmin):
    list_display = ('id', 'owner', 'destination', 'required_arrival_time', 'driver', 'can_be_shared', 'ride_status')
    list_display_links = ('id', 'owner')
    list_filter = ('owner', 'driver', 'can_be_shared')
    list_editable = ('can_be_shared',)
    search_fields = ('owner', 'destination', 'required_arrival_time',
                     'driver')
    list_per_page = 25


admin.site.register(Ride, RideAdmin)
