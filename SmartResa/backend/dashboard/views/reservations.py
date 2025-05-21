from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.db.models import Q
from datetime import timedelta
from ..models import Seat, Reservation
from ..forms import ReservationForm
from django.contrib.auth.decorators import login_required

def seat_selection(request):
    now = timezone.now()
    seats = Seat.objects.annotate(
        is_reserved=Q(
            reservation__end_time__gte=now,
            reservation__start_time__lte=now
        )
    ).order_by('number')
    
    return render(request, 'reservations/seat_selection.html', {
        'seats': seats,
        'current_time': now
    })

def create_reservation(request, seat_id):
    seat = get_object_or_404(Seat, id=seat_id)
    
    if request.method == 'POST':
        form = ReservationForm(request.POST)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.user = request.user
            reservation.seat = seat
            
            # Validate reservation constraints
            errors = validate_reservation(request.user, seat, reservation)
            if errors:
                for error in errors:
                    form.add_error(None, error)
                return render(request, 'reservations/create.html', 
                            {'form': form, 'seat': seat})

            try:
                reservation.save()
                seat.status = 'reserved'
                seat.save()
                messages.success(request, "Reservation successful!")
                return redirect('student_dashboard')
            except Exception as e:
                messages.error(request, f"Reservation failed: {str(e)}")
    
    else:
        form = ReservationForm(initial={
            'start_time': timezone.now(),
            'end_time': timezone.now() + timedelta(hours=2)
        })
    
    return render(request, 'reservations/create.html', {
        'form': form,
        'seat': seat
    })

def validate_reservation(user, seat, reservation):
    errors = []
    
    # Check seat availability
    if seat.status != 'available':
        errors.append("This seat is no longer available")
    
    # Check user role vs seat type
    if seat.seat_type == 'teacher' and user.role != 'teacher':
        errors.append("Only teachers can reserve teacher seats")
    
    # Check reservation duration
    max_hours = 8 if user.role == 'teacher' else {
        '3A': 2, '4A': 4, '5A': 6
    }.get(user.year, 0)
    
    duration = reservation.end_time - reservation.start_time
    if duration.total_seconds() < 1800:
        errors.append("Minimum reservation time is 30 minutes")
    elif duration.total_seconds() > max_hours * 3600:
        errors.append(f"Maximum reservation time: {max_hours} hours")
    
@login_required
def cancel_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, user=request.user)
    
    if request.method == 'POST':
        seat = reservation.seat
        seat.status = 'available'
        seat.save()
        reservation.delete()
        messages.success(request, "Reservation cancelled")
        return redirect('student_dashboard')
    
    return render(request, 'reservations/confirm_cancel.html', {'reservation': reservation})