from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from dashboard.models import CustomUser, Seat, Reservation

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rfid_access_check(request):
    rfid_id = request.data.get('rfid_id')
    seat_number = request.data.get('seat_number')
    
    try:
        user = CustomUser.objects.get(rfid_id=rfid_id)
        seat = Seat.objects.get(number=seat_number)
    except (CustomUser.DoesNotExist, Seat.DoesNotExist):
        return Response({'access': False, 'reason': 'Invalid credentials'}, 
                       status=status.HTTP_404_NOT_FOUND)

    valid_reservation = Reservation.objects.filter(
        user=user,
        seat=seat,
        start_time__lte=timezone.now(),
        end_time__gte=timezone.now()
    ).exists()

    return Response({
        'access': valid_reservation,
        'user_name': f"{user.first_name} {user.last_name}",
        'seat_number': seat.number,
        'valid_until': Reservation.objects.get(user=user, seat=seat).end_time if valid_reservation else None
    })

@api_view(['GET'])
def test_api(request):
    return Response({"status": "API working!"})