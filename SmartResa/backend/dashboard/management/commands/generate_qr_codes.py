# dashboard/management/commands/generate_qr_codes.py
from django.core.management.base import BaseCommand
from dashboard.models import Seat, QRCodeLink
from django.urls import reverse

class Command(BaseCommand):
    help = 'Generates QR codes for all seats'

    def handle(self, *args, **options):
        for seat in Seat.objects.all():
            qr_link, created = QRCodeLink.objects.get_or_create(
                seat=seat,
                defaults={'url': reverse('qr_scan', args=[seat.number])}
            )
            if created:
                qr_link.save()
                self.stdout.write(f'Created QR code for {seat.number}')