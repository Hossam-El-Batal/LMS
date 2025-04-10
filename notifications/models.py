from django.db import models
from users.models import User
from libraries.models import BookCopy


# Create your models here.

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('borrowed', 'Book Borrowed'),
        ('returned', 'Book Returned'),
        ('due_soon', 'Due Date Approaching'),
        ('overdue', 'Book Overdue'),
        ('available', 'Book Available'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    book_copy = models.ForeignKey(BookCopy, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.notification_type} for {self.user.username}"
