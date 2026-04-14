from django.core.management.base import BaseCommand
from django.utils import timezone
from routine.models import FacultyNotice, StudentNotification


class Command(BaseCommand):
    help = 'Delete expired faculty notices (older than their posted_date)'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Find expired notices
        expired_notices = FacultyNotice.objects.filter(posted_date__lt=today)
        
        expired_count = expired_notices.count()
        
        if expired_count > 0:
            # Delete associated notifications first
            StudentNotification.objects.filter(notice__in=expired_notices).delete()
            
            # Delete the notices
            expired_notices.delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {expired_count} expired notice(s) and their associated notifications.'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('No expired notices found.')
            )
