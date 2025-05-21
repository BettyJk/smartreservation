# dashboard/views/qr.py
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from ..models import Seat, QRCodeLink

def handle_qr_scan(request, seat_number):
    seat = get_object_or_404(Seat, number=seat_number)
    
    if request.user.is_authenticated:
        # Mobile reservation logic
        return redirect('mobile_reservation', seat_id=seat.id)
    
    # Show seat status to unauthenticated users
    return render(request, 'qr/seat_status.html', {'seat': seat})