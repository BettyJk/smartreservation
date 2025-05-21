# dashboard/models.py (optimized)
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class CustomUserManager(BaseUserManager):
    def create_user(self, email, first_name, last_name, role, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(
            email,
            first_name,
            last_name,
            'admin',
            password=password,
            **extra_fields
        )

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Administrator'),
    ]
    YEAR_CHOICES = [
        ('3A', '3rd Year'),
        ('4A', '4th Year'),
        ('5A', '5th Year'),
    ]

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    filiere = models.CharField(max_length=100, blank=True, null=True)
    year = models.CharField(max_length=2, choices=YEAR_CHOICES, blank=True, null=True)
    rfid_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def clean(self):
        if self.role == 'student':
            if not self.filiere:
                raise ValidationError('Filiere is required for students')
            if not self.year:
                raise ValidationError('Year is required for students')
        else:
            if self.filiere:
                raise ValidationError('Filiere should only be set for students')
            if self.year:
                raise ValidationError('Year should only be set for students')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
from django.db import models
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone

class Seat(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('occupied', 'Occupied'),
        ('blocked', 'Blocked'),
    ]
    SEAT_TYPE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]

    number = models.CharField(max_length=10, unique=True, help_text="Format: QR-S## or QR-T##")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    seat_type = models.CharField(max_length=10, choices=SEAT_TYPE_CHOICES)
    blocked_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.number} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        old_status = self.status
        super().save(*args, **kwargs)
        
        # Get active reservation if exists
        reservation = self.reservation_set.filter(
            end_time__gte=timezone.now()
        ).first()

        # Notify WebSocket group on status change
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "seats",
            {
                "type": "seat.update",
                "number": self.number,
                "status": self.status,
                "end_time": str(reservation.end_time) if reservation else None
            }
        )
class Reservation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.seat} ({self.start_time} to {self.end_time})"
# dashboard/models.py
import qrcode
from io import BytesIO
from django.core.files import File

class QRCodeLink(models.Model):
    seat = models.OneToOneField(Seat, on_delete=models.CASCADE)
    url = models.URLField()
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True)

    def save(self, *args, **kwargs):
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(self.url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to media storage
        buffer = BytesIO()
        img.save(buffer)
        filename = f'qr_{self.seat.number}.png'
        self.qr_code.save(filename, File(buffer), save=False)
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"QR Code for {self.seat.number}"
# dashboard/models.py
class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('reservation', 'New Reservation'),
        ('reminder', 'Reminder'),
        ('system', 'System Alert'),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)
    link = models.URLField(blank=True)  # For deep linking

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.user.email}"
# dashboard/models.py
class Course(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.code})"

class CourseSchedule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    day_of_week = models.IntegerField(choices=[
        (0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')
    ])
    start_time = models.TimeField()
    end_time = models.TimeField()
    seats = models.ManyToManyField(Seat)