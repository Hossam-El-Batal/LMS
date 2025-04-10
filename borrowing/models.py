from django.db import models

from django.db import models
from users.models import User
from libraries.models import BookCopy
from django.utils import timezone
from datetime import timedelta
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.conf import settings




class Borrowing(models.Model):
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrowings')
    transaction_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    total_penalty = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def calculate_penalties(self):
        """Calculate penalties for overdue items"""
        penalty_amount = 0

        DAILY_PENALTY_RATE = 1.00
        for item in self.items.all():
            if not item.returned_date and item.is_overdue():
                #days overdue calc
                days_overdue = (timezone.now().date() - item.due_date.date()).days
                item_penalty = days_overdue * DAILY_PENALTY_RATE
                penalty_amount += item_penalty

        self.total_penalty = penalty_amount
        self.save()

        return penalty_amount

    def update_status(self):
        """Update the borrowing status based on its items"""
        all_items = self.items.all()
        if not all_items:
            return

        # mark returned items
        if all(item.returned_date for item in all_items):
            self.status = 'returned'
        # mark as overdue items
        elif any(item.is_overdue() for item in all_items):
            self.status = 'overdue'
        else:
            self.status = 'active'

        self.save()

    @staticmethod
    def can_borrow_more(user):
        """Check if user can borrow more books (limit of 3 books)"""
        active_borrows = BorrowedItem.objects.filter(
            borrowing__user=user,
            returned_date__isnull=True
        ).count()

        return active_borrows < 3

    def __str__(self):
        return f"Borrowed by {self.user.username} on {self.transaction_date.strftime('%Y-%m-%d')}"


class BorrowedItem(models.Model):
    borrowing = models.ForeignKey(Borrowing, on_delete=models.CASCADE, related_name='items')
    book_copy = models.ForeignKey(BookCopy, on_delete=models.CASCADE, related_name='borrow_records')
    due_date = models.DateTimeField()
    returned_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.book_copy.book.title} due on {self.due_date.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):

        if self.due_date and not self.id:  # Only check on creation
            max_borrow_period = timezone.now() + timedelta(days=30)
            if self.due_date > max_borrow_period:
                raise ValidationError("Due date cannot be more than 1 month from today")

        if not self.returned_date:
            self.book_copy.status = 'borrowed'
        else:
            self.book_copy.status = 'available'
            if self.is_overdue():
                days_overdue = (self.returned_date.date() - self.due_date.date()).days
                DAILY_PENALTY_RATE = 1.00
                self.penalty_amount = days_overdue * DAILY_PENALTY_RATE

        self.book_copy.save()
        super().save(*args, **kwargs)

        # then update status
        self.borrowing.update_status()

    def is_overdue(self):
        """Check if the item is overdue"""
        if self.returned_date:
            return self.returned_date > self.due_date
        return timezone.now() > self.due_date

    def days_until_due(self):
        """Calculate days until due date"""
        if self.returned_date:
            return 0

        return (self.due_date.date() - timezone.now().date()).days


def send_borrow_confirmation_email(borrowing):
    """Send a confirmation email when books are borrowed"""
    subject = 'Books borrowed successfully'
    items_list = '\n'.join([
        f"- {item.book_copy.book.title} (Due: {item.due_date.strftime('%Y-%m-%d')})"
        for item in borrowing.items.all()
    ])

    message = f"""
    Dear {borrowing.user.username},

    This email confirms that you have borrowed the following books:

    {items_list}

    Please remember to return them by their due dates to avoid penalties.

    Thank you for using our library system!
    """

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [borrowing.user.email]

    # In development, this will be captured by Mailhog
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)


def send_due_date_reminder(borrowed_item):
    """Send a reminder when a book is due soon"""
    subject = 'Reminder: Book due date approaching'
    message = f"""
    Dear {borrowed_item.borrowing.user.username},

    This is a reminder that your borrowed book "{borrowed_item.book_copy.book.title}" 
    is due in {borrowed_item.days_until_due()} days on {borrowed_item.due_date.strftime('%Y-%m-%d')}.

    Please return it on time to avoid penalty fees.

    Thank you for using our library system!
    """

    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [borrowed_item.borrowing.user.email]

    # In development, this will be captured by Mailhog
    send_mail(subject, message, from_email, recipient_list, fail_silently=False)


# Signal handlers
def borrowing_post_save(sender, instance, created, **kwargs):
    """Send confirmation email when a new borrowing is created"""
    if created:
        send_borrow_confirmation_email(instance)
