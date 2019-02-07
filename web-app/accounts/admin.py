from django.contrib import admin

from .models import DriverProfile


class DriverProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'real_name', 'is_driver',
                    'vehicle_type', 'maximum_passengers', 'license_plate_number')
    list_display_links = ('id', 'real_name')
    list_filter = ('is_driver', 'vehicle_type')
    list_editable = ('is_driver',)
    search_fields = ('real_name', 'vehicle_type', 'maximum_passengers',
                     'license_plate_number')
    list_per_page = 25



admin.site.register(DriverProfile, DriverProfileAdmin)
