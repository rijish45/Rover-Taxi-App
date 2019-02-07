from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import auth, messages
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q
from django.core.mail import send_mail

from datetime import datetime

from accounts.utils import get_checkbox_input

from .utils import user_role_in_ride, str_to_datetime
from .models import Ride


def rides(request):
    """List all rides"""
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    
    user = get_object_or_404(User, id=request.user.id)
    rides_as_owner = user.rides_as_owner.all().order_by(
        'id').filter(~Q(ride_status='complete'))
    rides_as_driver = user.rides_as_driver.all().order_by(
        'id').filter(~Q(ride_status='complete'))
    rides_as_sharer = user.rides_as_sharer.all().order_by(
        'id').filter(~Q(ride_status='complete'))

    context = {
        'rides_as_owner': rides_as_owner,
        'rides_as_driver': rides_as_driver,
        'rides_as_sharer': rides_as_sharer,
    }

    return render(request, 'rides/rides.html', context)


def ride(request, ride_id):
    """Detail page for ride with ride_id"""
    # Authentication
    if not request.user.is_authenticated:
        return HttpResponse(status=401)

    user = get_object_or_404(User, id=request.user.id)
    ride = get_object_or_404(Ride, id=ride_id)
    
    user_role = user_role_in_ride(user, ride)
    if user_role == 'other':
        return HttpResponse(status=404)
    else:
        context = {
            'ride': ride,
        }
        return render(request, 'rides/ride.html', context)
        

def search(request):
    """Return search results"""
    # Authentication
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    # GET
    if request.method == 'GET':
        return render(request, 'rides/search.html')
    # POST
    if request.method == 'POST':
        search_as = request.POST.get('search_as')
        if search_as not in ['driver', 'sharer']:
            return HttpResponse(status=404)
        if search_as == 'driver':
            user = get_object_or_404(User, id=request.user.id)
            # search as driver, but doesn't have a driver account
            if not user.driverProfile.is_driver:
                messages(request, 'You are not a driver.')
                return redirect('dashboard')

            driver_vehicle_type = user.driverProfile.vehicle_type
            driver_special_vehicle_info = user.driverProfile.special_vehicle_info
            driver_maximum_passengers = user.driverProfile.maximum_passengers


            print('What is driver\'s vehicle:', driver_vehicle_type)

            rides = Ride.objects.order_by('-id').filter(
                Q(ride_status='open'),
                Q(requested_vehicle_type='') | Q(requested_vehicle_type=driver_vehicle_type),
                Q(special_request='') | Q(special_request=driver_special_vehicle_info),
                Q(passenger_number_in_total__lte=driver_maximum_passengers),
                ~Q(owner_id=user.id) & ~Q(sharers__id=user.id)
            )

            for ride in rides:
            	print(ride.requested_vehicle_type==driver_vehicle_type)

            print('How many rides:', len(rides))
            context = {
                'rides': rides,
                'search_as_driver': True,
            }
            return render(request, 'rides/search_results.html', context)
        # search as a sharer
        else:
            user = get_object_or_404(User, id=request.user.id)
            
            destination = request.POST['destination']
            number_of_passengers = int(request.POST['number_of_passengers'])
            earliest_arrival_time = str_to_datetime(
                request.POST['earliest_arrival_time']
            )
            latest_arrival_time = str_to_datetime(
                request.POST['latest_arrival_time']
            )
            
            rides = Ride.objects.order_by('-id').filter(
                Q(ride_status='open'),
                Q(can_be_shared=True),
                Q(passenger_number_in_total__lte=number_of_passengers),
                Q(destination=destination),
                Q(required_arrival_time__gte=earliest_arrival_time) & Q(
                    required_arrival_time__lte=latest_arrival_time),
                ~Q(owner_id=user.id) & ~Q(sharers__id=user.id) & ~Q(driver_id=user.id),
            )

            context = {
                'rides': rides,
                'search_as_sharer': True,
            }
            return render(request, 'rides/search_results.html', context)


def create(request):
    """Create a ride(as owner)"""
    # Authentication
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    # GET
    if request.method == 'GET':
        return render(request, 'rides/create.html')
    # POST
    if request.method == 'POST':
        user = get_object_or_404(User, id=request.user.id)
        
        destination = request.POST['destination']
        required_arrival_time = str_to_datetime(
            request.POST['arrival_time']
        )
        passenger_number_from_owner = request.POST['number_of_passengers']
        requested_vehicle_type = request.POST['vehicle_type']
        special_request = request.POST['special_request']
        can_be_shared = get_checkbox_input('can_be_shared', request)
        
        # create object
        Ride.objects.create(
            owner=user,
            destination=destination, required_arrival_time=required_arrival_time,
            passenger_number_from_owner=passenger_number_from_owner,
            passenger_number_in_total=passenger_number_from_owner,
            can_be_shared=can_be_shared, 
            requested_vehicle_type=requested_vehicle_type, 
            special_request=special_request,
        )
        # send message & return
        messages.success(request, 'You have successfully made a request.')
        return redirect('rides')
    

def edit(request, ride_id):
    """Edit a ride"""
    # Authentication
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    # Identify User's role
    user = get_object_or_404(User, id=request.user.id)
    ride = get_object_or_404(Ride, id=ride_id)
    user_role = user_role_in_ride(user, ride)
    # GET: Display ride information
    if request.method == 'GET':
        context = {
            'ride': ride,
            'edit_as': user_role,
        }
        return render(request, 'rides/edit.html', context)
    # POST: Update ride information(for owner only), driver and sharer user different methods below
    if request.method == 'POST' and user_role == 'owner' and ride.ride_status == 'open':
        # get form inputs
        destination = request.POST['destination']
        required_arrival_time = str_to_datetime(
            request.POST['arrival_time']
        )
        passenger_number_from_owner = int(request.POST['number_of_passengers'])
        requested_vehicle_type = request.POST['vehicle_type']
        special_request = request.POST['special_request']
        can_be_shared = get_checkbox_input('can_be_shared', request)
        # Update ride information
        ride.destination = destination
        ride.required_arrival_time = required_arrival_time
        ride.can_be_shared = can_be_shared
        ride.requested_vehicle_type = requested_vehicle_type
        ride.special_request = special_request

        old_passenger_number_from_owner = ride.passenger_number_from_owner # pay special attention
        ride.passenger_number_from_owner = passenger_number_from_owner  # pay special attention
        ride.passenger_number_in_total += (passenger_number_from_owner - old_passenger_number_from_owner)

        ride.save()
        return redirect('rides')


def confirm(request, ride_id):
    """Confirm the ride with ride_id"""
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    if request.method != 'POST':
        return HttpResponse(status=404)

    user = get_object_or_404(User, id=request.user.id)
    ride = get_object_or_404(Ride, id=ride_id)
    if not user.driverProfile.is_driver:
        return HttpResponse(status=404)
    if ride.ride_status != 'open':
        return HttpResponse(status=404)
    
    ride.driver = user
    ride.ride_status = 'confirm'
    ride.save()
    
    email_list = [ride.owner.email]
    for sharer in ride.sharers.all():
        email_list.append(sharer.email)
    send_mail(
      'Ride Confirmed',
      'Your ride has been confirmed by driver' + ride.driver.driverProfile.real_name,
      'rover_admin@rover.co',
      email_list,
      fail_silently=True,
    )
    messages.success(request, 'You have successfully confirmed the ride.')
    return redirect('rides')


def complete(request, ride_id):
    """Complete the ride with ride_id"""
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    if request.method != 'POST':
        return HttpResponse(status=404)
    
    user = get_object_or_404(User, id=request.user.id)
    ride = get_object_or_404(Ride, id=ride_id)
    user_role = user_role_in_ride(user, ride)
    if not user.driverProfile.is_driver:
        return HttpResponse(status=404)
    if user_role != 'driver':
        return HttpResponse(status=404)
    
    ride.ride_status = 'complete'
    ride.save()
    messages.success(request, 'You have successfully completed the ride.')
    return redirect('rides')


def share(request, ride_id):
    """Share the ride with ride_id"""
    if not request.user.is_authenticated:
        return HttpResponse(status=401)
    if request.method != 'POST':
        return HttpResponse(status=404)

    user = get_object_or_404(User, id=request.user.id)
    ride = get_object_or_404(Ride, id=ride_id)
    if not ride.can_be_shared:
        return HttpResponse(status=404)

    new_number_of_passengers = int(request.POST['number_of_passengers'])
    if user not in ride.sharers.all():
        ride.sharers.add(user)

    # bug fix: object is null when init, object.get is not supported
    if not ride.sharer_id_and_passenger_number_pair:
        ride.sharer_id_and_passenger_number_pair = {}
    # bug fix: dictionary key should always be string
    record = ride.sharer_id_and_passenger_number_pair.get(str(user.id))
    old_number_of_passengers = record['number_of_passengers'] if record else 0
    ride.passenger_number_in_total += (
        new_number_of_passengers - old_number_of_passengers
    )
    ride.sharer_id_and_passenger_number_pair[user.id] = {
        'username': user.username,
        'number_of_passengers': new_number_of_passengers
    }
    ride.save()
    messages.success(request, 'You have joined the ride.')
    return redirect('rides')

