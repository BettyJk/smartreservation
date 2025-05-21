# dashboard/views/admin.py
from django.utils import timezone
from django.db.models import Count, Q
from django.db.models.functions import TruncHour
from django.shortcuts import render
from django.http import HttpResponse
import csv
from ..models import Seat, Reservation
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from datetime import timedelta
from ..forms import BlockSeatForm
from ..models import Seat
def admin_dashboard(request):
    # Seat statistics using aggregation
    seat_stats = Seat.objects.aggregate(
        total=Count('id'),
        available=Count('id', filter=Q(status='available')),
        reserved=Count('id', filter=Q(status='reserved')),
        occupied=Count('id', filter=Q(status='occupied')),
        blocked=Count('id', filter=Q(status='blocked')),
    )

    # Current reservations
    current_reservations = Reservation.objects.filter(
        end_time__gte=timezone.now()
    ).order_by('-created_at')[:10]

    # Busiest hours analysis
    busiest_hours = Reservation.objects.annotate(
        hour=TruncHour('start_time')
    ).values('hour').annotate(
        count=Count('id')
    ).order_by('-count')[:5]

    # Recent reservations (last 7 days)
    recent_reservations = Reservation.objects.filter(
        start_time__gte=timezone.now() - timezone.timedelta(days=7)
    ).order_by('-start_time')

    context = {
        **seat_stats,
        'current_reservations': current_reservations,
        'busiest_hours': busiest_hours,
        'recent_reservations': recent_reservations[:10],  # Last 10
    }
    
    return render(request, 'dashboards/admin.html', context)

def export_reservations_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="reservations.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['User', 'Seat', 'Start Time', 'End Time', 'Status'])
    
    for res in Reservation.objects.all().select_related('user', 'seat'):
        writer.writerow([
            res.user.email,
            res.seat.number,
            res.start_time.strftime("%Y-%m-%d %H:%M"),
            res.end_time.strftime("%Y-%m-%d %H:%M"),
            res.seat.status
        ])
    
    return response
@staff_member_required
def block_seat(request, seat_id):
    seat = get_object_or_404(Seat, id=seat_id)
    
    if request.method == 'POST':
        form = BlockSeatForm(request.POST)
        if form.is_valid():
            seat.status = 'blocked'
            seat.blocked_reason = form.cleaned_data['reason']
            seat.blocked_until = timezone.now() + timedelta(
                hours=form.cleaned_data['duration']
            )
            seat.save()
            return redirect('admin_dashboard')
    else:
        form = BlockSeatForm()
    
    return render(request, 'admin/block_seat.html', {'form': form, 'seat': seat})