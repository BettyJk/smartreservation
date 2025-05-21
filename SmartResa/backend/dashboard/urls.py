from django.urls import path
from .views.auth import register_view, custom_login, custom_logout
from .views.dashboards import StudentDashboard, TeacherDashboard, AdminDashboard
from .views.reservations import seat_selection, create_reservation
from .views.qr import handle_qr_scan
from .views.admin import export_reservations_csv
from django.http import JsonResponse
urlpatterns = [
    # Auth URLs
    path('register/', register_view, name='register'),
    path('login/', custom_login, name='login'),
    path('logout/', custom_logout, name='logout'),
    
    # Dashboard URLs
    path('student/', StudentDashboard.as_view(), name='student_dashboard'),
    path('teacher/', TeacherDashboard.as_view(), name='teacher_dashboard'),
    path('admin-dashboard/', AdminDashboard.as_view(), name='admin_dashboard'),
    
    # Reservation system
    path('seats/', seat_selection, name='seat_selection'),
    path('reserve/<int:seat_id>/', create_reservation, name='create_reservation'),
    path('qr/<str:seat_number>/', handle_qr_scan, name='qr_scan'),
    path('export-reservations/', export_reservations_csv, name='export_reservations_csv'),
    path('test/', lambda request: JsonResponse({'status': 'ok'}), name='test-api'),
]