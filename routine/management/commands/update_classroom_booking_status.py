from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
from routine.models import ClassroomBooking


class Command(BaseCommand):
    help = 'Updates classroom booking status for expired bookings'

    def handle(self, *args, **options):
        """
        Update booking statuses:
        - If end_time has passed and status is CONFIRMED/PENDING/ONGOING -> mark as COMPLETED
        - If start_time <= current_time <= end_time and status is CONFIRMED -> mark as ONGOING
        """
        now = timezone.now()
        updated_count = 0
        ongoing_count = 0

        # Get all active bookings
        active_bookings = ClassroomBooking.objects.filter(
            status__in=['CONFIRMED', 'PENDING', 'ONGOING']
        )

        for booking in active_bookings:
            # Check if booking has expired
            booking_end_naive = datetime.combine(booking.booking_date, booking.end_time)
            booking_start_naive = datetime.combine(booking.booking_date, booking.start_time)
            
            # Make them timezone-aware
            booking_end = timezone.make_aware(booking_end_naive)
            booking_start = timezone.make_aware(booking_start_naive)

            if now > booking_end and booking.status != 'COMPLETED':
                # Mark as completed
                booking.status = 'COMPLETED'
                booking.save()
                updated_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Completed: {booking.classroom} - {booking.booking_date} '
                        f'{booking.start_time}-{booking.end_time}'
                    )
                )

            # Check if booking is currently ongoing
            elif booking_start <= now <= booking_end:
                if booking.status != 'ONGOING':
                    booking.status = 'ONGOING'
                    booking.save()
                    ongoing_count += 1
                    self.stdout.write(
                        self.style.WARNING(
                            f'⟳ Ongoing: {booking.classroom} - {booking.booking_date} '
                            f'{booking.start_time}-{booking.end_time}'
                        )
                    )

        # Print summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Summary: Updated {updated_count} bookings to COMPLETED, '
                f'{ongoing_count} bookings marked as ONGOING'
            )
        )
