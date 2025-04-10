from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from borrowing.models import BorrowedItem, send_due_date_reminder


class Command(BaseCommand):
    help = 'Send reminders for books due in the next 3 days'

    def handle(self, *args, **options):
        now = timezone.now()
        three_days_later = now + timedelta(days=3)

        due_soon_items = BorrowedItem.objects.filter(
            returned_date__isnull=True,
            due_date__gte=now,
            due_date__lte=three_days_later
        )

        count = 0
        for item in due_soon_items:
            send_due_date_reminder(item)
            count += 1

        self.stdout.write(
            self.style.SUCCESS(f'Successfully sent {count} reminders')
        )