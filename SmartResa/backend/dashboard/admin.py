# dashboard/admin.py
from django.contrib import admin
from .models import CustomUser
from .models import CustomUser, Seat, Reservation

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'role')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('role', 'year')
class SeatAdmin(admin.ModelAdmin):
    list_display = ('number', 'seat_type', 'status')
    list_filter = ('seat_type', 'status')

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('user', 'seat', 'start_time', 'end_time')
    search_fields = ('user__email', 'seat__number')

admin.site.register(Seat, SeatAdmin)
admin.site.register(Reservation, ReservationAdmin)
admin.site.register(CustomUser, CustomUserAdmin)