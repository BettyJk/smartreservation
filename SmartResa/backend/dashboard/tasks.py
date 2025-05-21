# dashboard/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import Reservation, Seat, CourseSchedule
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def check_reservation_expiry():
    """Automatically expire reservations and update seat status"""
    now = timezone.now()
    expired_reservations = Reservation.objects.filter(end_time__lte=now)
    
    for reservation in expired_reservations:
        try:
            with transaction.atomic():
                seat = reservation.seat
                seat.status = 'available'
                seat.blocked_reason = None
                seat.save()
                reservation.delete()
                
                # Send WebSocket update
                send_seat_update(seat, f"Reservation expired for {seat.number}")
                
                # Send user notification
                send_user_notification(
                    reservation.user,
                    "Reservation Expired",
                    f"Your reservation for {seat.number} has expired"
                )
                
        except Exception as e:
            print(f"Error processing reservation {reservation.id}: {str(e)}")

@shared_task
def auto_block_seats():
    """Automatically block seats during scheduled courses"""
    now = timezone.localtime()
    current_time = now.time()
    current_day = now.weekday()
    
    try:
        # Block seats for ongoing courses
        active_courses = CourseSchedule.objects.filter(
            day_of_week=current_day,
            start_time__lte=current_time,
            end_time__gte=current_time
        ).prefetch_related('seats')
        
        for course in active_courses:
            for seat in course.seats.all():
                if seat.status != 'blocked':
                    seat.status = 'blocked'
                    seat.blocked_reason = f"Course: {course.course.name} ({course.start_time}-{course.end_time})"
                    seat.save()
                    send_seat_update(seat, f"Seat blocked for {course.course.name}")
        
        # Unblock seats after course hours
        expired_courses = CourseSchedule.objects.filter(
            day_of_week=current_day,
            end_time__lt=current_time
        ).prefetch_related('seats')
        
        for course in expired_courses:
            for seat in course.seats.all():
                if seat.status == 'blocked' and seat.blocked_reason.startswith("Course:"):
                    seat.status = 'available'
                    seat.blocked_reason = None
                    seat.save()
                    send_seat_update(seat, "Course ended, seat available")

    except Exception as e:
        print(f"Error in auto_block_seats: {str(e)}")

def send_seat_update(seat, message=None):
    """Helper function to send seat updates via WebSocket"""
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "seats",
            {
                "type": "seat.update",
                "number": seat.number,
                "status": seat.status,
                "message": message,
                "blocked_reason": seat.blocked_reason,
                "updated_at": str(timezone.now())
            }
        )
    except Exception as e:
        print(f"WebSocket error: {str(e)}")

def send_user_notification(user, title, message):
    """Helper function to send user notifications"""
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"notifications_{user.id}",
            {
                "type": "send.notification",
                "title": title,
                "message": message,
                "timestamp": str(timezone.now())
            }
        )
    except Exception as e:
        print(f"Notification error: {str(e)}")
@shared_task
def debug_task():
    print("CELERY IS WORKING!")
    return "SUCCESS"